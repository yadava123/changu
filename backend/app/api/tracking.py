from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.models import Delivery, DeliveryStatus, Driver, EmergencyProvider, EmergencyRequest, EmergencyStatus, Parcel, ParcelStatus, Ride, RideStatus, User, UserRole
from app.schemas.location import LocationResponse, LocationUpdate
from app.websocket.manager import manager

router = APIRouter(prefix="/api/tracking", tags=["tracking"])
driver_router = APIRouter(prefix="/api/driver", tags=["driver location"])
provider_router = APIRouter(prefix="/api/provider", tags=["provider location"])


def publish_location(db, user_id: int, entity_type: str, entity_id: int, latitude: float, longitude: float):
    db.info.setdefault("tracking_events", []).append((user_id, {"type": "LOCATION_UPDATED", "entity_type": entity_type, "entity_id": entity_id, "data": {"latitude": latitude, "longitude": longitude}}))


def location_payload(latitude, longitude, updated_at):
    return LocationResponse(latitude=latitude, longitude=longitude, updated_at=updated_at)


@driver_router.post("/location", response_model=LocationResponse)
def update_driver_location(payload: LocationUpdate, user: User = Depends(require_role(UserRole.DRIVER)), db: Session = Depends(get_db)):
    driver = db.scalar(select(Driver).where(Driver.user_id == user.id, Driver.is_active.is_(True)))
    if not driver:
        raise HTTPException(403, "Active driver account required")
    if not driver.is_online:
        raise HTTPException(400, "Go online before sharing location")
    driver.latitude, driver.longitude = payload.latitude, payload.longitude
    deliveries = db.scalars(select(Delivery).where(Delivery.driver_id == driver.id, Delivery.status.in_([DeliveryStatus.ACCEPTED, DeliveryStatus.PICKED_UP, DeliveryStatus.OUT_FOR_DELIVERY]))).all()
    for delivery in deliveries:
        db.info.setdefault("tracking_events", []).append((delivery.order.user_id, {"type": "LOCATION_UPDATED", "entity_type": "ORDER", "entity_id": delivery.order_id, "data": {"latitude": payload.latitude, "longitude": payload.longitude}}))
    parcels = db.scalars(select(Parcel).where(Parcel.driver_id == driver.id, Parcel.status.in_([ParcelStatus.ACCEPTED, ParcelStatus.PICKED_UP, ParcelStatus.IN_TRANSIT, ParcelStatus.OUT_FOR_DELIVERY]))).all()
    for parcel in parcels:
        db.info.setdefault("tracking_events", []).append((parcel.customer_id, {"type": "LOCATION_UPDATED", "entity_type": "PARCEL", "entity_id": parcel.id, "data": {"latitude": payload.latitude, "longitude": payload.longitude}}))
    rides = db.scalars(select(Ride).where(Ride.driver_id == driver.id, Ride.status.in_([RideStatus.DRIVER_ASSIGNED, RideStatus.DRIVER_ARRIVING, RideStatus.DRIVER_ARRIVED, RideStatus.RIDE_STARTED]))).all()
    for ride in rides:
        db.info.setdefault("tracking_events", []).append((ride.customer_id, {"type": "LOCATION_UPDATED", "entity_type": "RIDE", "entity_id": ride.id, "data": {"latitude": payload.latitude, "longitude": payload.longitude}}))
    publish_location(db, user.id, "DRIVER", driver.id, payload.latitude, payload.longitude)
    db.commit()
    return location_payload(driver.latitude, driver.longitude, driver.updated_at)


@provider_router.post("/location", response_model=LocationResponse)
def update_provider_location(payload: LocationUpdate, user: User = Depends(require_role(UserRole.EMERGENCY_PROVIDER)), db: Session = Depends(get_db)):
    provider = db.scalar(select(EmergencyProvider).where(EmergencyProvider.user_id == user.id, EmergencyProvider.is_active.is_(True), EmergencyProvider.is_verified.is_(True)))
    if not provider:
        raise HTTPException(403, "Verified active provider account required")
    if not provider.is_online:
        raise HTTPException(400, "Go online before sharing location")
    provider.latitude, provider.longitude = payload.latitude, payload.longitude
    requests = db.scalars(select(EmergencyRequest).where(EmergencyRequest.provider_id == provider.id, EmergencyRequest.status.in_([EmergencyStatus.PROVIDER_ASSIGNED, EmergencyStatus.ACCEPTED, EmergencyStatus.ON_THE_WAY, EmergencyStatus.ARRIVED, EmergencyStatus.IN_SERVICE]))).all()
    for request in requests:
        db.info.setdefault("tracking_events", []).append((request.user_id, {"type": "LOCATION_UPDATED", "entity_type": "SIREN", "entity_id": request.id, "data": {"latitude": payload.latitude, "longitude": payload.longitude}}))
    publish_location(db, user.id, "PROVIDER", provider.id, payload.latitude, payload.longitude)
    db.commit()
    return location_payload(provider.latitude, provider.longitude, provider.updated_at)


def tracking_for_customer(user: User, kind: str, item_id: int, db: Session):
    if kind == "parcel":
        item = db.scalar(select(Parcel).where(Parcel.id == item_id, Parcel.customer_id == user.id))
        driver_id = item.driver_id if item else None
        entity_type = "PARCEL"
    elif kind == "ride":
        item = db.scalar(select(Ride).where(Ride.id == item_id, Ride.customer_id == user.id))
        driver_id = item.driver_id if item else None
        entity_type = "RIDE"
    elif kind == "siren":
        item = db.scalar(select(EmergencyRequest).where(EmergencyRequest.id == item_id, EmergencyRequest.user_id == user.id))
        driver_id = None
        entity_type = "SIREN"
        provider_id = item.provider_id if item else None
        provider = db.get(EmergencyProvider, provider_id) if provider_id else None
        if not item:
            raise HTTPException(404, "Tracking resource not found")
        return {"entity_type": entity_type, "entity_id": item.id, "status": item.status, "location": location_payload(provider.latitude, provider.longitude, provider.updated_at).model_dump() if provider and provider.latitude is not None and provider.longitude is not None else None}
    else:
        raise HTTPException(404, "Tracking resource not found")
    if not item:
        raise HTTPException(404, "Tracking resource not found")
    driver = db.get(Driver, driver_id) if driver_id else None
    return {"entity_type": entity_type, "entity_id": item.id, "status": item.status, "location": location_payload(driver.latitude, driver.longitude, driver.updated_at).model_dump() if driver and driver.latitude is not None and driver.longitude is not None else None}


@router.get("/orders/{order_id}")
def order_tracking(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    delivery = db.scalar(select(Delivery).join(Delivery.order).where(Delivery.order_id == order_id, Delivery.order.has(user_id=user.id)))
    if not delivery:
        raise HTTPException(404, "Tracking resource not found")
    driver = db.get(Driver, delivery.driver_id) if delivery.driver_id else None
    return {"entity_type": "ORDER", "entity_id": order_id, "status": delivery.status, "location": location_payload(driver.latitude, driver.longitude, driver.updated_at).model_dump() if driver and driver.latitude is not None and driver.longitude is not None else None}


@router.get("/{kind}/{item_id}")
def customer_tracking(kind: str, item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return tracking_for_customer(user, kind, item_id, db)


@router.get("/provider/requests/{request_id}")
def provider_tracking(request_id: int, user: User = Depends(require_role(UserRole.EMERGENCY_PROVIDER)), db: Session = Depends(get_db)):
    provider = db.scalar(select(EmergencyProvider).where(EmergencyProvider.user_id == user.id))
    item = db.scalar(select(EmergencyRequest).where(EmergencyRequest.id == request_id, EmergencyRequest.provider_id == provider.id))
    if not item:
        raise HTTPException(404, "Tracking resource not found")
    return {"entity_type": "SIREN", "entity_id": item.id, "status": item.status, "location": {"latitude": item.latitude, "longitude": item.longitude} if item.latitude is not None and item.longitude is not None else None}


from sqlalchemy import event
from sqlalchemy.orm import Session as SqlAlchemySession


@event.listens_for(SqlAlchemySession, "after_commit")
def publish_tracking_events(session):
    for user_id, message in session.info.pop("tracking_events", []):
        manager.send_to_user_sync(user_id, message)
