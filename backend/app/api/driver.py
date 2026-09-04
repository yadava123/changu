from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.models import Delivery, DeliveryStatus, Driver, DriverApplication, DriverApplicationStatus, Order, OrderStatus, Parcel, ParcelStatus, PaymentMethod, PaymentStatus, Restaurant, Ride, RideStatus, User, UserRole
from app.schemas.driver import DeliveryResponse, DriverApplicationRequest, DriverApplicationResponse, DriverResponse, DriverStatusRequest
from app.services.financial_service import settle_earning
from app.services.notification_service import NotificationService
from app.services.growth_service import award_order_points

router = APIRouter(prefix="/api/driver", tags=["driver"])
driver_only = require_role(UserRole.DRIVER)


def get_driver(user: User, db: Session) -> Driver:
    driver = db.scalar(select(Driver).where(Driver.user_id == user.id))
    if not driver or not driver.is_active:
        raise HTTPException(status_code=403, detail="Active driver account required")
    return driver


@router.post("/applications", response_model=DriverApplicationResponse, status_code=201)
def apply(payload: DriverApplicationRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role == UserRole.DRIVER:
        raise HTTPException(status_code=409, detail="Your driver account is already active.")
    existing = db.scalar(select(DriverApplication).where(DriverApplication.user_id == user.id, DriverApplication.status == DriverApplicationStatus.PENDING))
    if existing:
        raise HTTPException(status_code=409, detail="You already have a pending driver application.")
    application = DriverApplication(user_id=user.id, **payload.model_dump())
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/applications/me", response_model=DriverApplicationResponse)
def my_application(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    application = db.scalar(select(DriverApplication).where(DriverApplication.user_id == user.id).order_by(DriverApplication.created_at.desc()))
    if not application:
        raise HTTPException(status_code=404, detail="Driver application not found")
    return application


@router.get("/status", response_model=dict)
def status(user: User = Depends(driver_only), db: Session = Depends(get_db)):
    driver = get_driver(user, db)
    busy = db.scalar(select(Delivery.id).where(Delivery.driver_id == driver.id, Delivery.status.in_([DeliveryStatus.ACCEPTED, DeliveryStatus.PICKED_UP, DeliveryStatus.OUT_FOR_DELIVERY]))) is not None
    return {"is_online": driver.is_online, "is_active": driver.is_active, "availability": "BUSY" if busy else "ONLINE" if driver.is_online else "OFFLINE"}


@router.post("/status", response_model=dict)
def update_status(payload: DriverStatusRequest, user: User = Depends(driver_only), db: Session = Depends(get_db)):
    driver = get_driver(user, db)
    if not payload.is_online and db.scalar(select(Delivery.id).where(Delivery.driver_id == driver.id, Delivery.status.in_([DeliveryStatus.ACCEPTED, DeliveryStatus.PICKED_UP, DeliveryStatus.OUT_FOR_DELIVERY]))) is not None:
        raise HTTPException(400, "Complete the active delivery before going offline")
    driver.is_online = payload.is_online
    db.commit()
    return {"is_online": driver.is_online, "is_active": driver.is_active, "availability": "ONLINE" if driver.is_online else "OFFLINE"}


@router.get("/dashboard")
def dashboard(user: User = Depends(driver_only), db: Session = Depends(get_db)):
    driver = get_driver(user, db)
    today = datetime.now().date().isoformat()
    completed = db.scalar(select(func.count(Delivery.id)).where(Delivery.driver_id == driver.id, Delivery.status == DeliveryStatus.DELIVERED)) or 0
    pending = db.scalar(select(func.count(Delivery.id)).where(Delivery.driver_id == driver.id, Delivery.status.in_([DeliveryStatus.ACCEPTED, DeliveryStatus.PICKED_UP, DeliveryStatus.OUT_FOR_DELIVERY]))) or 0
    today_deliveries = db.scalar(select(func.count(Delivery.id)).where(Delivery.driver_id == driver.id, func.date(Delivery.created_at) == today)) or 0
    earnings = db.scalar(select(func.coalesce(func.sum(Delivery.delivery_earning), 0)).where(Delivery.driver_id == driver.id, Delivery.status == DeliveryStatus.DELIVERED, func.date(Delivery.delivered_at) == today)) or 0
    return {"today_deliveries": today_deliveries, "completed_deliveries": completed, "pending_deliveries": pending, "today_earnings": earnings, "is_online": driver.is_online}


@router.get("/deliveries/available", response_model=list[DeliveryResponse])
def available(user: User = Depends(driver_only), db: Session = Depends(get_db)):
    driver = get_driver(user, db)
    if not driver.is_online:
        return []
    return db.scalars(select(Delivery).where(Delivery.status == DeliveryStatus.AVAILABLE).order_by(Delivery.created_at)).all()


@router.get("/deliveries", response_model=list[DeliveryResponse])
def deliveries(user: User = Depends(driver_only), db: Session = Depends(get_db)):
    driver = get_driver(user, db)
    return db.scalars(select(Delivery).where(Delivery.driver_id == driver.id).order_by(Delivery.created_at.desc())).all()


def own_delivery(delivery_id: int, driver: Driver, db: Session) -> Delivery:
    delivery = db.scalar(select(Delivery).where(Delivery.id == delivery_id, Delivery.driver_id == driver.id))
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


def has_other_transport_job(driver_id: int, db: Session) -> bool:
    parcel = db.scalar(select(Parcel.id).where(Parcel.driver_id == driver_id, Parcel.status.in_([ParcelStatus.ACCEPTED, ParcelStatus.PICKED_UP, ParcelStatus.IN_TRANSIT, ParcelStatus.OUT_FOR_DELIVERY])))
    ride = db.scalar(select(Ride.id).where(Ride.driver_id == driver_id, Ride.status.in_([RideStatus.DRIVER_ASSIGNED, RideStatus.DRIVER_ARRIVING, RideStatus.DRIVER_ARRIVED, RideStatus.RIDE_STARTED])))
    return parcel is not None or ride is not None


@router.post("/deliveries/{delivery_id}/accept", response_model=DeliveryResponse)
def accept(delivery_id: int, user: User = Depends(driver_only), db: Session = Depends(get_db)):
    driver = get_driver(user, db)
    if not driver.is_online:
        raise HTTPException(status_code=400, detail="Go online before accepting deliveries")
    if db.scalar(select(Delivery.id).where(Delivery.driver_id == driver.id, Delivery.status.in_([DeliveryStatus.ACCEPTED, DeliveryStatus.PICKED_UP, DeliveryStatus.OUT_FOR_DELIVERY]))) is not None:
        raise HTTPException(status_code=409, detail="Complete your active delivery before accepting another")
    if has_other_transport_job(driver.id, db):
        raise HTTPException(status_code=409, detail="Complete your active transport job before accepting a delivery")
    delivery = db.scalar(select(Delivery).where(Delivery.id == delivery_id).with_for_update())
    if not delivery or delivery.status != DeliveryStatus.AVAILABLE:
        raise HTTPException(status_code=409, detail="Delivery is no longer available.")
    delivery.driver_id = driver.id
    delivery.status = DeliveryStatus.ACCEPTED
    delivery.accepted_at = datetime.utcnow()
    order = db.get(Order, delivery.order_id)
    order.status = OrderStatus.DRIVER_ASSIGNED
    NotificationService.from_template(db, order.user_id, "DRIVER_ASSIGNED", "driver_assigned", "ORDER", order.id,
                                      f"order:{order.id}:driver-assigned", order_number=order.order_number)
    NotificationService.from_template(db, order.user_id, "DRIVER_ACCEPTED", "driver_accepted", "DELIVERY", delivery.id,
                                      f"delivery:{delivery.id}:driver-accepted")
    vendor_user_id = order.seller_id
    if order.restaurant_id:
        vendor_user_id = db.scalar(select(Restaurant.owner_id).where(Restaurant.id == order.restaurant_id))
    if vendor_user_id:
        NotificationService.from_template(db, vendor_user_id, "DRIVER_ASSIGNED", "driver_assigned", "ORDER", order.id,
                                          f"order:{order.id}:vendor-driver-assigned", order_number=order.order_number)
    db.commit()
    db.refresh(delivery)
    return delivery


def transition(delivery_id: int, user: User, expected: DeliveryStatus, target: DeliveryStatus, db: Session, timestamp: str | None = None, commit: bool = True):
    driver = get_driver(user, db)
    delivery = own_delivery(delivery_id, driver, db)
    if delivery.status != expected:
        raise HTTPException(status_code=400, detail=f"Invalid delivery status transition from {delivery.status}")
    delivery.status = target
    if timestamp:
        setattr(delivery, timestamp, datetime.utcnow())
    order = db.get(Order, delivery.order_id)
    if target == DeliveryStatus.OUT_FOR_DELIVERY:
        order.status = OrderStatus.OUT_FOR_DELIVERY
        NotificationService.from_template(db, order.user_id, "ORDER_OUT_FOR_DELIVERY", "order_out_for_delivery", "ORDER", order.id,
                                          f"order:{order.id}:out-for-delivery", order_number=order.order_number)
    if commit:
        db.commit()
    db.refresh(delivery)
    return delivery


@router.post("/deliveries/{delivery_id}/pickup", response_model=DeliveryResponse)
def pickup(delivery_id: int, user: User = Depends(driver_only), db: Session = Depends(get_db)):
    return transition(delivery_id, user, DeliveryStatus.ACCEPTED, DeliveryStatus.PICKED_UP, db, "picked_up_at")


@router.post("/deliveries/{delivery_id}/out-for-delivery", response_model=DeliveryResponse)
def out_for_delivery(delivery_id: int, user: User = Depends(driver_only), db: Session = Depends(get_db)):
    return transition(delivery_id, user, DeliveryStatus.PICKED_UP, DeliveryStatus.OUT_FOR_DELIVERY, db, "out_for_delivery_at")


@router.post("/deliveries/{delivery_id}/complete", response_model=DeliveryResponse)
def complete(delivery_id: int, user: User = Depends(driver_only), db: Session = Depends(get_db)):
    delivery = transition(delivery_id, user, DeliveryStatus.OUT_FOR_DELIVERY, DeliveryStatus.DELIVERED, db, "delivered_at", commit=False)
    order = db.get(Order, delivery.order_id)
    order.status = OrderStatus.DELIVERED
    if order.payment_method == PaymentMethod.CASH_ON_DELIVERY:
        order.payment_status = PaymentStatus.PAID
    settle_earning(db, user, "DELIVERY", delivery.id, delivery.delivery_earning)
    vendor_user_id = order.seller_id
    if order.restaurant_id:
        vendor_user_id = db.scalar(select(Restaurant.owner_id).where(Restaurant.id == order.restaurant_id))
    if vendor_user_id:
        vendor = db.get(User, vendor_user_id)
        if vendor:
            settle_earning(db, vendor, "ORDER", order.id, order.total_amount)
    NotificationService.from_template(db, order.user_id, "ORDER_DELIVERED", "order_delivered", "ORDER", order.id,
                                      f"order:{order.id}:delivered", order_number=order.order_number)
    award_order_points(db, order.user_id, order.id, order.total_amount)
    db.commit()
    return delivery
