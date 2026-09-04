from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import require_role
from app.db.session import get_db
from app.models import Delivery, DeliveryStatus, Driver, DriverApplication, DriverApplicationStatus, User, UserRole
from app.schemas.driver import DriverApplicationResponse, DriverResponse
from app.schemas.vendor import AdminApplicationDecision

router = APIRouter(prefix="/api/admin", tags=["admin drivers"])
admin_only = require_role(UserRole.ADMIN)


@router.get("/driver-applications", response_model=list[DriverApplicationResponse])
def applications(user: User = Depends(admin_only), db: Session = Depends(get_db)):
    return db.scalars(select(DriverApplication).order_by(DriverApplication.created_at.desc())).all()


@router.patch("/driver-applications/{application_id}", response_model=DriverApplicationResponse)
def decide(application_id: int, payload: AdminApplicationDecision, user: User = Depends(admin_only), db: Session = Depends(get_db)):
    application = db.get(DriverApplication, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Driver application not found")
    if application.status != DriverApplicationStatus.PENDING or payload.status.value not in {DriverApplicationStatus.APPROVED.value, DriverApplicationStatus.REJECTED.value}:
        raise HTTPException(status_code=400, detail="Invalid driver application decision")
    application.status = DriverApplicationStatus(payload.status.value)
    application.admin_notes = payload.admin_notes
    if payload.status.value == DriverApplicationStatus.APPROVED.value:
        application.user.role = UserRole.DRIVER
        if not db.scalar(select(Driver).where(Driver.user_id == application.user_id)):
            db.add(Driver(user_id=application.user_id, full_name=application.full_name, phone=application.phone, email=application.email, vehicle_type=application.vehicle_type.value, vehicle_number=application.vehicle_number, license_number=application.license_number, address=application.address, area=application.area, city=application.city, state=application.state, pincode=application.pincode))
    db.commit()
    db.refresh(application)
    return application


@router.get("/drivers", response_model=list[DriverResponse])
def drivers(user: User = Depends(admin_only), db: Session = Depends(get_db)):
    return db.scalars(select(Driver).order_by(Driver.created_at.desc())).all()


@router.get("/drivers/{driver_id}", response_model=DriverResponse)
def driver(driver_id: int, user: User = Depends(admin_only), db: Session = Depends(get_db)):
    item = db.get(Driver, driver_id)
    if not item:
        raise HTTPException(status_code=404, detail="Driver not found")
    return item


@router.patch("/drivers/{driver_id}/status", response_model=DriverResponse)
def status(driver_id: int, payload: dict, user: User = Depends(admin_only), db: Session = Depends(get_db)):
    item = db.get(Driver, driver_id)
    if not item:
        raise HTTPException(status_code=404, detail="Driver not found")
    item.is_active = bool(payload.get("is_active"))
    if not item.is_active:
        item.is_online = False
    db.commit()
    db.refresh(item)
    return item
