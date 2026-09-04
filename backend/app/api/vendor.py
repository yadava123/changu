from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.models import Delivery, DeliveryStatus, Driver, FoodItem, Order, OrderItem, OrderStatus, Product, Restaurant, User, UserRole, Vendor, VendorApplication, ApplicationStatus
from app.schemas.vendor import VendorApplicationRequest, VendorApplicationResponse, VendorResponse, VendorStoreUpdate
from app.schemas.vendor_catalog import VendorFoodCreate, VendorFoodResponse, VendorProductCreate, VendorProductResponse
from app.schemas.commerce import OrderResponse
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/api/vendor", tags=["vendor"])
vendor_only = require_role(UserRole.VENDOR)


def get_vendor(user: User, db: Session) -> Vendor:
    vendor = db.scalar(select(Vendor).where(Vendor.user_id == user.id, Vendor.is_active.is_(True)))
    if not vendor:
        raise HTTPException(status_code=403, detail="Active vendor account required")
    return vendor


def get_restaurant(vendor: Vendor, db: Session) -> Restaurant | None:
    return db.scalar(select(Restaurant).where(Restaurant.owner_id == vendor.user_id))


@router.post("/applications", response_model=VendorApplicationResponse, status_code=201)
def apply(payload: VendorApplicationRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role == UserRole.VENDOR:
        raise HTTPException(status_code=409, detail="Your vendor account is already active.")
    existing = db.scalar(select(VendorApplication).where(VendorApplication.user_id == user.id, VendorApplication.status == ApplicationStatus.PENDING))
    if existing:
        raise HTTPException(status_code=409, detail="You already have a pending vendor application.")
    application = VendorApplication(user_id=user.id, **payload.model_dump())
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/applications/me", response_model=VendorApplicationResponse)
def my_application(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    application = db.scalar(select(VendorApplication).where(VendorApplication.user_id == user.id).order_by(VendorApplication.created_at.desc()))
    if not application:
        raise HTTPException(status_code=404, detail="Vendor application not found")
    return application


@router.get("/store", response_model=VendorResponse)
def store(user: User = Depends(vendor_only), db: Session = Depends(get_db)):
    return get_vendor(user, db)


@router.post("/store", response_model=VendorResponse, status_code=201)
def create_store(payload: VendorStoreUpdate, user: User = Depends(vendor_only), db: Session = Depends(get_db)):
    existing = db.scalar(select(Vendor).where(Vendor.user_id == user.id))
    if existing:
        raise HTTPException(status_code=409, detail="Vendor store already exists")
    values = payload.model_dump()
    values["business_type"] = values["business_type"].value
    vendor = Vendor(user_id=user.id, **values)
    db.add(vendor)
    db.flush()
    db.commit()
    db.refresh(vendor)
    return vendor


@router.patch("/store", response_model=VendorResponse)
def update_store(payload: VendorStoreUpdate, user: User = Depends(vendor_only), db: Session = Depends(get_db)):
    vendor = get_vendor(user, db)
    values = payload.model_dump()
    values["business_type"] = values["business_type"].value
    for key, value in values.items():
        setattr(vendor, key, value)
    db.commit()
    db.refresh(vendor)
    return vendor


@router.get("/products", response_model=list[VendorProductResponse])
def products(user: User = Depends(vendor_only), db: Session = Depends(get_db)):
    get_vendor(user, db)
    return db.scalars(select(Product).where(Product.seller_id == user.id).order_by(Product.created_at.desc())).all()


@router.post("/products", response_model=VendorProductResponse, status_code=201)
def create_product(payload: VendorProductCreate, user: User = Depends(vendor_only), db: Session = Depends(get_db)):
    get_vendor(user, db)
    product = Product(seller_id=user.id, **payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/products/{product_id}", response_model=VendorProductResponse)
def product(product_id: int, user: User = Depends(vendor_only), db: Session = Depends(get_db)):
    get_vendor(user, db)
    item = db.scalar(select(Product).where(Product.id == product_id, Product.seller_id == user.id))
    if not item:
        raise HTTPException(status_code=404, detail="Product not found")
    return item


@router.patch("/products/{product_id}", response_model=VendorProductResponse)
def update_product(product_id: int, payload: VendorProductCreate, user: User = Depends(vendor_only), db: Session = Depends(get_db)):
    item = product(product_id, user, db)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/products/{product_id}", response_model=VendorProductResponse)
def disable_product(product_id: int, user: User = Depends(vendor_only), db: Session = Depends(get_db)):
    item = product(product_id, user, db)
    item.is_available = False
    db.commit()
    db.refresh(item)
    return item


@router.get("/food", response_model=list[VendorFoodResponse])
def food(user: User = Depends(vendor_only), db: Session = Depends(get_db)):
    vendor = get_vendor(user, db)
    restaurant = get_restaurant(vendor, db)
    if not restaurant:
        return []
    return db.scalars(select(FoodItem).where(FoodItem.restaurant_id == restaurant.id).order_by(FoodItem.created_at.desc())).all()


@router.post("/food", response_model=VendorFoodResponse, status_code=201)
def create_food(payload: VendorFoodCreate, user: User = Depends(vendor_only), db: Session = Depends(get_db)):
    vendor = get_vendor(user, db)
    restaurant = get_restaurant(vendor, db)
    if not restaurant:
        raise HTTPException(status_code=400, detail="Create a vendor store before adding food")
    item = FoodItem(restaurant_id=restaurant.id, name=payload.name, description=payload.description, price=payload.price, category=payload.category, image_url=payload.image_url, is_available=payload.is_available)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/dashboard")
def dashboard(user: User = Depends(vendor_only), db: Session = Depends(get_db)):
    vendor = get_vendor(user, db)
    restaurant = get_restaurant(vendor, db)
    ownership = or_(Order.seller_id == user.id, Order.restaurant_id == restaurant.id if restaurant else False)
    total = db.scalar(select(func.count(Order.id)).where(ownership)) or 0
    pending = db.scalar(select(func.count(Order.id)).where(ownership, Order.status == OrderStatus.PENDING)) or 0
    completed = db.scalar(select(func.count(Order.id)).where(ownership, Order.status == OrderStatus.DELIVERED)) or 0
    today = db.scalar(select(func.count(Order.id)).where(ownership, func.date(Order.created_at) == date.today().isoformat())) or 0
    sales = db.scalar(select(func.coalesce(func.sum(Order.total_amount), 0)).where(ownership, func.date(Order.created_at) == date.today().isoformat())) or 0
    product_count = db.scalar(select(func.count(Product.id)).where(Product.seller_id == user.id)) or 0
    low_stock = db.scalar(select(func.count(Product.id)).where(Product.seller_id == user.id, Product.stock_quantity.between(1, 5))) or 0
    return {"total_orders": total, "pending_orders": pending, "completed_orders": completed, "today_orders": today, "today_sales": sales, "total_products": product_count, "low_stock_products": low_stock}


@router.get("/orders", response_model=list[OrderResponse])
def vendor_orders(user: User = Depends(vendor_only), db: Session = Depends(get_db)):
    vendor = get_vendor(user, db)
    restaurant = get_restaurant(vendor, db)
    ownership = or_(Order.seller_id == user.id, Order.restaurant_id == restaurant.id if restaurant else False)
    return db.scalars(select(Order).options(selectinload(Order.items)).where(ownership).order_by(Order.created_at.desc())).all()


@router.get("/orders/{order_id}", response_model=OrderResponse)
def vendor_order(order_id: int, user: User = Depends(vendor_only), db: Session = Depends(get_db)):
    order = next((item for item in vendor_orders(user, db) if item.id == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(order_id: int, payload: dict, user: User = Depends(vendor_only), db: Session = Depends(get_db)):
    order = vendor_order(order_id, user, db)
    try:
        requested = OrderStatus(payload.get("status"))
    except (ValueError, TypeError):
        raise HTTPException(status_code=422, detail="Invalid order status") from None
    allowed = {OrderStatus.PENDING: OrderStatus.CONFIRMED, OrderStatus.CONFIRMED: OrderStatus.PREPARING, OrderStatus.PREPARING: OrderStatus.READY_FOR_PICKUP}
    if allowed.get(order.status) != requested:
        raise HTTPException(status_code=400, detail="Invalid order status transition")
    db_order = db.get(Order, order.id)
    db_order.status = requested
    if requested == OrderStatus.READY_FOR_PICKUP and not db.scalar(select(Delivery).where(Delivery.order_id == db_order.id)):
        db.add(Delivery(order_id=db_order.id, status=DeliveryStatus.AVAILABLE, pickup_address="Vendor pickup location", delivery_address=db_order.delivery_address, delivery_earning=30))
        drivers = db.scalars(select(Driver).where(Driver.is_active.is_(True), Driver.is_online.is_(True))).all()
        for driver in drivers:
            NotificationService.from_template(db, driver.user_id, "NEW_DELIVERY", "driver_task", "ORDER", db_order.id,
                                              f"order:{db_order.id}:driver-task:{driver.id}", order_number=db_order.order_number)
    notification_names = {
        OrderStatus.CONFIRMED: ("ORDER_CONFIRMED", "order_accepted"),
        OrderStatus.PREPARING: ("ORDER_PREPARING", "order_preparing"),
        OrderStatus.READY_FOR_PICKUP: ("ORDER_READY", "order_ready"),
    }
    notification_type, template_name = notification_names[requested]
    NotificationService.from_template(db, db_order.user_id, notification_type, template_name, "ORDER", db_order.id,
                                      f"order:{db_order.id}:{requested.value}", order_number=db_order.order_number)
    db.commit()
    return vendor_order(order.id, user, db)
