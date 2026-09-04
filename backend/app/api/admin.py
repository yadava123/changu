from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import require_role
from app.db.session import get_db
from app.models import User, UserRole, Vendor, VendorApplication, ApplicationStatus
from app.schemas.vendor import AdminApplicationDecision, VendorApplicationResponse

router = APIRouter(prefix="/api/admin", tags=["admin"])
admin_only = require_role(UserRole.ADMIN)


@router.get("/vendor-applications", response_model=list[VendorApplicationResponse])
def applications(user: User = Depends(admin_only), db: Session = Depends(get_db)):
    return db.scalars(select(VendorApplication).order_by(VendorApplication.created_at.desc())).all()


@router.patch("/vendor-applications/{application_id}", response_model=VendorApplicationResponse)
def decide(application_id: int, payload: AdminApplicationDecision, user: User = Depends(admin_only), db: Session = Depends(get_db)):
    application = db.get(VendorApplication, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Vendor application not found")
    if application.status != ApplicationStatus.PENDING:
        raise HTTPException(status_code=400, detail="Application has already been decided")
    if payload.status not in {ApplicationStatus.APPROVED, ApplicationStatus.REJECTED}:
        raise HTTPException(status_code=400, detail="Decision must be APPROVED or REJECTED")
    application.status = payload.status
    application.admin_notes = payload.admin_notes
    if payload.status == ApplicationStatus.APPROVED:
        application.user.role = UserRole.VENDOR
        vendor = db.scalar(select(Vendor).where(Vendor.user_id == application.user_id))
        if not vendor:
            vendor = Vendor(user_id=application.user_id, business_name=application.business_name, business_type=application.business_type.value, description=application.description, phone=application.phone, email=application.email, address=application.address, area=application.area, city=application.city, state=application.state, pincode=application.pincode)
            db.add(vendor)
    db.commit()
    db.refresh(application)
    return application
