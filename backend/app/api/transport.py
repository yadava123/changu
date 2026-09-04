from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.models import Delivery, DeliveryStatus, Driver, Parcel, ParcelStatus, PaymentStatus, Ride, RideStatus, User, UserRole
from app.schemas.transport import ParcelCreate, ParcelResponse, RideCreate, RideResponse
from app.services.notification_service import NotificationService
from app.services.financial_service import settle_earning

parcel_router=APIRouter(prefix="/api/parcels",tags=["parcels"]); ride_router=APIRouter(prefix="/api/rides",tags=["rides"]); driver_transport_router=APIRouter(prefix="/api/driver",tags=["driver transport"])
def parcel_price(weight): return 50 + min(int(weight * 10), 500)
def ride_fare(ride_type): return {"STANDARD":80,"PREMIUM":140,"XL":200}.get(ride_type.upper(),80)

@parcel_router.post("",response_model=ParcelResponse,status_code=201)
def create_parcel(payload:ParcelCreate,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    item=Parcel(customer_id=user.id,price=parcel_price(payload.weight_kg),**payload.model_dump());db.add(item);db.flush();NotificationService.create_notification(db,user.id,"Parcel created","Your parcel request has been created.","SYSTEM","PARCEL",item.id,f"parcel:{item.id}:created");db.commit();db.refresh(item);return item
@parcel_router.get("",response_model=list[ParcelResponse])
def list_parcels(user:User=Depends(get_current_user),db:Session=Depends(get_db)): return db.scalars(select(Parcel).where(Parcel.customer_id==user.id).order_by(Parcel.created_at.desc())).all()
@parcel_router.get("/{parcel_id}",response_model=ParcelResponse)
def parcel(parcel_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    item=db.scalar(select(Parcel).where(Parcel.id==parcel_id,Parcel.customer_id==user.id));
    if not item: raise HTTPException(404,"Parcel not found")
    return item
@parcel_router.post("/{parcel_id}/cancel",response_model=ParcelResponse)
def cancel_parcel(parcel_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    item=parcel(parcel_id,user,db)
    if item.status not in {ParcelStatus.PENDING,ParcelStatus.ACCEPTED}: raise HTTPException(400,"Parcel cannot be cancelled")
    if item.payment_status == PaymentStatus.PAID: raise HTTPException(400,"Paid parcel requires refund processing before cancellation")
    item.status=ParcelStatus.CANCELLED;db.commit();return item

@ride_router.post("",response_model=RideResponse,status_code=201)
def create_ride(payload:RideCreate,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    active_statuses=[RideStatus.REQUESTED,RideStatus.DRIVER_ASSIGNED,RideStatus.DRIVER_ARRIVING,RideStatus.DRIVER_ARRIVED,RideStatus.RIDE_STARTED]
    if db.scalar(select(Ride.id).where(Ride.customer_id==user.id,Ride.status.in_(active_statuses))):
        raise HTTPException(409,"Complete or cancel your active ride before requesting another")
    item=Ride(customer_id=user.id,fare=ride_fare(payload.ride_type),**payload.model_dump());db.add(item);db.flush();NotificationService.create_notification(db,user.id,"Ride requested","Your ride request has been created.","SYSTEM","RIDE",item.id,f"ride:{item.id}:created");db.commit();db.refresh(item);return item
@ride_router.get("",response_model=list[RideResponse])
def list_rides(user:User=Depends(get_current_user),db:Session=Depends(get_db)): return db.scalars(select(Ride).where(Ride.customer_id==user.id).order_by(Ride.created_at.desc())).all()
@ride_router.get("/{ride_id}",response_model=RideResponse)
def ride(ride_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    item=db.scalar(select(Ride).where(Ride.id==ride_id,Ride.customer_id==user.id));
    if not item: raise HTTPException(404,"Ride not found")
    return item
@ride_router.post("/{ride_id}/cancel",response_model=RideResponse)
def cancel_ride(ride_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    item=ride(ride_id,user,db)
    if item.status not in {RideStatus.REQUESTED,RideStatus.DRIVER_ASSIGNED}: raise HTTPException(400,"Ride cannot be cancelled")
    item.status=RideStatus.CANCELLED
    if item.driver_id:
        driver=db.get(Driver,item.driver_id)
        if driver:
            NotificationService.create_notification(db,driver.user_id,"Ride cancelled","The customer cancelled this ride.","SYSTEM","RIDE",item.id,f"ride:{item.id}:cancelled:customer")
    db.commit();return item

def driver_record(user,db):
    driver=db.scalar(select(Driver).where(Driver.user_id==user.id,Driver.is_active.is_(True)))
    if not driver: raise HTTPException(403,"Active driver account required")
    if not driver.is_online: raise HTTPException(400,"Go online before using transport requests")
    return driver
def driver_has_active_job(driver_id,db):
    delivery = db.scalar(select(Delivery.id).where(Delivery.driver_id==driver_id,Delivery.status.in_([DeliveryStatus.ACCEPTED,DeliveryStatus.PICKED_UP,DeliveryStatus.OUT_FOR_DELIVERY])))
    parcel = db.scalar(select(Parcel.id).where(Parcel.driver_id==driver_id,Parcel.status.in_([ParcelStatus.ACCEPTED,ParcelStatus.PICKED_UP,ParcelStatus.IN_TRANSIT,ParcelStatus.OUT_FOR_DELIVERY])))
    ride = db.scalar(select(Ride.id).where(Ride.driver_id==driver_id,Ride.status.in_([RideStatus.DRIVER_ASSIGNED,RideStatus.DRIVER_ARRIVING,RideStatus.DRIVER_ARRIVED,RideStatus.RIDE_STARTED])))
    return delivery is not None or parcel is not None or ride is not None
@driver_transport_router.get("/parcels/available",response_model=list[ParcelResponse])
def available_parcels(user:User=Depends(require_role(UserRole.DRIVER)),db:Session=Depends(get_db)):
    driver=driver_record(user,db)
    if driver_has_active_job(driver.id,db): return []
    return db.scalars(select(Parcel).where(Parcel.status==ParcelStatus.PENDING,Parcel.payment_status==PaymentStatus.PAID,Parcel.driver_id.is_(None))).all()
@driver_transport_router.post("/parcels/{parcel_id}/accept",response_model=ParcelResponse)
def accept_parcel(parcel_id:int,user:User=Depends(require_role(UserRole.DRIVER)),db:Session=Depends(get_db)):
    driver=driver_record(user,db)
    if driver_has_active_job(driver.id,db): raise HTTPException(409,"Complete your active transport job before accepting another")
    item=db.scalar(select(Parcel).where(Parcel.id==parcel_id).with_for_update())
    if not item or item.status!=ParcelStatus.PENDING or item.driver_id is not None: raise HTTPException(409,"Parcel is no longer available")
    item.driver_id=driver.id;item.status=ParcelStatus.ACCEPTED;NotificationService.create_notification(db,item.customer_id,"Parcel driver assigned","A driver has accepted your parcel.","SYSTEM","PARCEL",item.id,f"parcel:{item.id}:accepted");db.commit();db.refresh(item);return item
@driver_transport_router.post("/parcels/{parcel_id}/pickup",response_model=ParcelResponse)
def pickup_parcel(parcel_id:int,user:User=Depends(require_role(UserRole.DRIVER)),db:Session=Depends(get_db)):
    return transport_transition(Parcel,ParcelStatus.ACCEPTED,ParcelStatus.PICKED_UP,parcel_id,user,db)
@driver_transport_router.post("/parcels/{parcel_id}/transit",response_model=ParcelResponse)
def transit_parcel(parcel_id:int,user:User=Depends(require_role(UserRole.DRIVER)),db:Session=Depends(get_db)):
    return transport_transition(Parcel,ParcelStatus.PICKED_UP,ParcelStatus.IN_TRANSIT,parcel_id,user,db)
@driver_transport_router.post("/parcels/{parcel_id}/out-for-delivery",response_model=ParcelResponse)
def out_for_delivery_parcel(parcel_id:int,user:User=Depends(require_role(UserRole.DRIVER)),db:Session=Depends(get_db)):
    return transport_transition(Parcel,ParcelStatus.IN_TRANSIT,ParcelStatus.OUT_FOR_DELIVERY,parcel_id,user,db)
@driver_transport_router.post("/parcels/{parcel_id}/complete",response_model=ParcelResponse)
def complete_parcel(parcel_id:int,user:User=Depends(require_role(UserRole.DRIVER)),db:Session=Depends(get_db)):
    item = transport_transition(Parcel,ParcelStatus.OUT_FOR_DELIVERY,ParcelStatus.DELIVERED,parcel_id,user,db,commit=False)
    settle_earning(db, user, "PARCEL", item.id, item.price)
    db.commit()
    return item
@driver_transport_router.get("/rides/available",response_model=list[RideResponse])
def available_rides(user:User=Depends(require_role(UserRole.DRIVER)),db:Session=Depends(get_db)):
    driver=driver_record(user,db)
    if driver_has_active_job(driver.id,db): return []
    return db.scalars(select(Ride).where(Ride.status==RideStatus.REQUESTED,Ride.driver_id.is_(None))).all()
@driver_transport_router.post("/rides/{ride_id}/accept",response_model=RideResponse)
def accept_ride(ride_id:int,user:User=Depends(require_role(UserRole.DRIVER)),db:Session=Depends(get_db)):
    driver=driver_record(user,db)
    if driver_has_active_job(driver.id,db): raise HTTPException(409,"Complete your active transport job before accepting another")
    item=db.scalar(select(Ride).where(Ride.id==ride_id).with_for_update())
    if not item or item.status!=RideStatus.REQUESTED or item.driver_id is not None: raise HTTPException(409,"Ride is no longer available")
    item.driver_id=driver.id;item.status=RideStatus.DRIVER_ASSIGNED;NotificationService.create_notification(db,item.customer_id,"Ride driver assigned","A driver has accepted your ride.","SYSTEM","RIDE",item.id,f"ride:{item.id}:assigned");db.commit();db.refresh(item);return item
@driver_transport_router.post("/rides/{ride_id}/cancel",response_model=RideResponse)
def cancel_driver_ride(ride_id:int,user:User=Depends(require_role(UserRole.DRIVER)),db:Session=Depends(get_db)):
    driver=driver_record(user,db)
    item=db.scalar(select(Ride).where(Ride.id==ride_id,Ride.driver_id==driver.id).with_for_update())
    if not item: raise HTTPException(404,"Ride not found")
    if item.status not in {RideStatus.DRIVER_ASSIGNED,RideStatus.DRIVER_ARRIVING,RideStatus.DRIVER_ARRIVED}: raise HTTPException(400,"Ride cannot be cancelled")
    item.status=RideStatus.CANCELLED
    NotificationService.create_notification(db,item.customer_id,"Ride cancelled","Your driver cancelled the ride.","SYSTEM","RIDE",item.id,f"ride:{item.id}:cancelled:driver")
    db.commit();db.refresh(item);return item
@driver_transport_router.post("/rides/{ride_id}/arriving",response_model=RideResponse)
def arriving_ride(ride_id:int,user:User=Depends(require_role(UserRole.DRIVER)),db:Session=Depends(get_db)): return transport_transition(Ride,RideStatus.DRIVER_ASSIGNED,RideStatus.DRIVER_ARRIVING,ride_id,user,db)
@driver_transport_router.post("/rides/{ride_id}/arrived",response_model=RideResponse)
def arrived_ride(ride_id:int,user:User=Depends(require_role(UserRole.DRIVER)),db:Session=Depends(get_db)): return transport_transition(Ride,RideStatus.DRIVER_ARRIVING,RideStatus.DRIVER_ARRIVED,ride_id,user,db)
@driver_transport_router.post("/rides/{ride_id}/start",response_model=RideResponse)
def start_ride(ride_id:int,user:User=Depends(require_role(UserRole.DRIVER)),db:Session=Depends(get_db)): return transport_transition(Ride,RideStatus.DRIVER_ARRIVED,RideStatus.RIDE_STARTED,ride_id,user,db)
@driver_transport_router.post("/rides/{ride_id}/complete",response_model=RideResponse)
def complete_ride(ride_id:int,user:User=Depends(require_role(UserRole.DRIVER)),db:Session=Depends(get_db)):
    item = transport_transition(Ride,RideStatus.RIDE_STARTED,RideStatus.RIDE_COMPLETED,ride_id,user,db,commit=False)
    settle_earning(db, user, "RIDE", item.id, item.fare)
    db.commit()
    return item

def transport_transition(model,expected,target,item_id,user,db,commit=True):
    driver=driver_record(user,db); item=db.scalar(select(model).where(model.id==item_id,model.driver_id==driver.id).with_for_update())
    if not item: raise HTTPException(404,"Transport request not found")
    if item.status!=expected: raise HTTPException(400,f"Invalid status transition from {item.status}")
    item.status=target
    kind = "parcel" if model is Parcel else "ride"
    NotificationService.create_notification(db,item.customer_id,f"{kind.title()} status updated",f"Your {kind} is now {target.value.replace('_', ' ').lower()}.","SYSTEM",kind.upper(),item.id,f"{kind}:{item.id}:{target.value}")
    if commit:
        db.commit()
    db.refresh(item)
    return item