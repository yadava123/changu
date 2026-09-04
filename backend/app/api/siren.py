from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.models import ApplicationStatus, EmergencyPriority, EmergencyProvider, EmergencyRequest, EmergencyStatus, EmergencyType, ProviderApplication, ProviderType, User, UserRole
from app.schemas.siren import EmergencyRequestCreate, EmergencyRequestResponse, ProviderApplicationRequest, ProviderApplicationResponse, ProviderStatusRequest
from app.schemas.vendor import AdminApplicationDecision
from app.services.notification_service import NotificationService

customer_router=APIRouter(prefix="/api/emergency",tags=["siren"]); provider_router=APIRouter(prefix="/api/provider",tags=["siren provider"]); admin_router=APIRouter(prefix="/api/admin",tags=["siren admin"])
matching={EmergencyType.VEHICLE_BREAKDOWN:ProviderType.MECHANIC,EmergencyType.MECHANIC:ProviderType.MECHANIC,EmergencyType.FUEL_EMERGENCY:ProviderType.FUEL,EmergencyType.TOWING:ProviderType.TOWING,EmergencyType.AMBULANCE_ASSISTANCE:ProviderType.AMBULANCE,EmergencyType.DOCTOR_ASSISTANCE:ProviderType.DOCTOR,EmergencyType.EMERGENCY_MEDICINE:ProviderType.PHARMACY,EmergencyType.BLOOD_DONOR:ProviderType.BLOOD_NETWORK,EmergencyType.OTHER:ProviderType.OTHER}
def next_number(db): return f"CHGS{10001 + (db.scalar(select(func.count(EmergencyRequest.id))) or 0):05d}"
def provider_for(user,db):
    p=db.scalar(select(EmergencyProvider).where(EmergencyProvider.user_id==user.id))
    if not p or not p.is_verified or not p.is_active: raise HTTPException(403,"Verified active provider account required")
    return p

@customer_router.post("/requests",response_model=EmergencyRequestResponse,status_code=201)
def create_request(payload:EmergencyRequestCreate,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    active_statuses=[EmergencyStatus.CREATED,EmergencyStatus.SEARCHING,EmergencyStatus.PROVIDER_ASSIGNED,EmergencyStatus.ACCEPTED,EmergencyStatus.ON_THE_WAY,EmergencyStatus.ARRIVED,EmergencyStatus.IN_SERVICE]
    if db.scalar(select(EmergencyRequest.id).where(EmergencyRequest.user_id==user.id,EmergencyRequest.status.in_(active_statuses))):
        raise HTTPException(409,"Complete or cancel your active Siren request before creating another")
    r=EmergencyRequest(request_number=next_number(db),user_id=user.id,status=EmergencyStatus.SEARCHING,**payload.model_dump()); db.add(r); db.flush()
    NotificationService.from_template(db,user.id,"SIREN_REQUEST_CREATED","siren_created","SIREN",r.id,f"siren:{r.id}:created")
    provider_type=matching.get(r.emergency_type)
    providers=db.scalars(select(EmergencyProvider).where(EmergencyProvider.provider_type==provider_type,EmergencyProvider.is_verified.is_(True),EmergencyProvider.is_active.is_(True),EmergencyProvider.is_online.is_(True))).all()
    for provider in providers:
        NotificationService.from_template(db,provider.user_id,"NEW_SIREN_REQUEST","siren_provider","SIREN",r.id,f"siren:{r.id}:provider:{provider.id}")
    db.commit(); db.refresh(r); return r
@customer_router.get("/requests",response_model=list[EmergencyRequestResponse])
def my_requests(user:User=Depends(get_current_user),db:Session=Depends(get_db)): return db.scalars(select(EmergencyRequest).where(EmergencyRequest.user_id==user.id).order_by(EmergencyRequest.created_at.desc())).all()
@customer_router.get("/requests/{request_id}",response_model=EmergencyRequestResponse)
def get_request(request_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    r=db.scalar(select(EmergencyRequest).where(EmergencyRequest.id==request_id,EmergencyRequest.user_id==user.id))
    if not r: raise HTTPException(404,"Emergency request not found")
    return r
@customer_router.post("/requests/{request_id}/cancel",response_model=EmergencyRequestResponse)
def cancel_request(request_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    r=get_request(request_id,user,db)
    if r.status in {EmergencyStatus.ARRIVED,EmergencyStatus.IN_SERVICE,EmergencyStatus.RESOLVED,EmergencyStatus.CANCELLED}: raise HTTPException(400,"Request cannot be cancelled now")
    r.status=EmergencyStatus.CANCELLED; r.cancelled_at=datetime.utcnow()
    if r.provider_id:
        provider=db.get(EmergencyProvider,r.provider_id)
        if provider: NotificationService.create_notification(db,provider.user_id,"Siren request cancelled","The customer cancelled this request.","SYSTEM","SIREN",r.id,f"siren:{r.id}:cancelled:customer")
    db.commit(); return r

@provider_router.post("/applications",response_model=ProviderApplicationResponse,status_code=201)
def apply_provider(payload:ProviderApplicationRequest,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    if user.role==UserRole.EMERGENCY_PROVIDER: raise HTTPException(409,"Your provider account is already active.")
    if db.scalar(select(ProviderApplication).where(ProviderApplication.user_id==user.id,ProviderApplication.status==ApplicationStatus.PENDING)): raise HTTPException(409,"You already have a pending provider application.")
    a=ProviderApplication(user_id=user.id,**payload.model_dump()); db.add(a); db.commit(); db.refresh(a); return a
@provider_router.get("/applications/me",response_model=ProviderApplicationResponse)
def provider_application(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    a=db.scalar(select(ProviderApplication).where(ProviderApplication.user_id==user.id).order_by(ProviderApplication.created_at.desc()))
    if not a: raise HTTPException(404,"Provider application not found")
    return a
@provider_router.get("/status")
def provider_status(user:User=Depends(require_role(UserRole.EMERGENCY_PROVIDER)),db:Session=Depends(get_db)):
    p=provider_for(user,db); busy=db.scalar(select(EmergencyRequest.id).where(EmergencyRequest.provider_id==p.id,EmergencyRequest.status.in_([EmergencyStatus.ACCEPTED,EmergencyStatus.ON_THE_WAY,EmergencyStatus.ARRIVED,EmergencyStatus.IN_SERVICE]))) is not None; return {"is_verified":p.is_verified,"is_active":p.is_active,"is_online":p.is_online,"availability":"BUSY" if busy else "ONLINE" if p.is_online else "OFFLINE"}
@provider_router.post("/status")
def update_provider_status(payload:ProviderStatusRequest,user:User=Depends(require_role(UserRole.EMERGENCY_PROVIDER)),db:Session=Depends(get_db)):
    p=provider_for(user,db)
    if not payload.is_online and db.scalar(select(EmergencyRequest.id).where(EmergencyRequest.provider_id==p.id,EmergencyRequest.status.in_([EmergencyStatus.ACCEPTED,EmergencyStatus.ON_THE_WAY,EmergencyStatus.ARRIVED,EmergencyStatus.IN_SERVICE]))) is not None: raise HTTPException(400,"Resolve the active request before going offline")
    p.is_online=payload.is_online; db.commit(); return {"is_verified":p.is_verified,"is_active":p.is_active,"is_online":p.is_online,"availability":"ONLINE" if p.is_online else "OFFLINE"}
@provider_router.get("/requests/available",response_model=list[EmergencyRequestResponse])
def available_requests(user:User=Depends(require_role(UserRole.EMERGENCY_PROVIDER)),db:Session=Depends(get_db)):
    p=provider_for(user,db)
    if not p.is_online:return []
    types=[key for key,value in matching.items() if value==p.provider_type]
    return db.scalars(select(EmergencyRequest).where(EmergencyRequest.status==EmergencyStatus.SEARCHING,EmergencyRequest.emergency_type.in_(types))).all()
@provider_router.get("/requests",response_model=list[EmergencyRequestResponse])
def provider_requests(user:User=Depends(require_role(UserRole.EMERGENCY_PROVIDER)),db:Session=Depends(get_db)):
    p=provider_for(user,db); return db.scalars(select(EmergencyRequest).where(EmergencyRequest.provider_id==p.id).order_by(EmergencyRequest.created_at.desc())).all()
@provider_router.post("/requests/{request_id}/accept",response_model=EmergencyRequestResponse)
def accept_request(request_id:int,user:User=Depends(require_role(UserRole.EMERGENCY_PROVIDER)),db:Session=Depends(get_db)):
    p=provider_for(user,db)
    if not p.is_online: raise HTTPException(400,"Go online before accepting requests")
    if db.scalar(select(EmergencyRequest.id).where(EmergencyRequest.provider_id==p.id,EmergencyRequest.status.in_([EmergencyStatus.ACCEPTED,EmergencyStatus.ON_THE_WAY,EmergencyStatus.ARRIVED,EmergencyStatus.IN_SERVICE]))) is not None: raise HTTPException(409,"Complete your active request before accepting another")
    r=db.scalar(select(EmergencyRequest).where(EmergencyRequest.id==request_id).with_for_update())
    if not r or r.status!=EmergencyStatus.SEARCHING: raise HTTPException(409,"This request is no longer available.")
    if matching.get(r.emergency_type)!=p.provider_type: raise HTTPException(403,"This request does not match your provider type")
    r.provider_id=p.id; r.status=EmergencyStatus.PROVIDER_ASSIGNED; r.assigned_at=datetime.utcnow(); db.flush(); r.status=EmergencyStatus.ACCEPTED; r.accepted_at=datetime.utcnow()
    NotificationService.from_template(db,r.user_id,"SIREN_PROVIDER_ACCEPTED","siren_accepted","SIREN",r.id,f"siren:{r.id}:accepted")
    db.commit(); return r

def transition(request_id,user,target,expected,stamp,db):
    p=provider_for(user,db); r=db.scalar(select(EmergencyRequest).where(EmergencyRequest.id==request_id,EmergencyRequest.provider_id==p.id))
    if not r: raise HTTPException(404,"Emergency request not found")
    if r.status!=expected: raise HTTPException(400,f"Invalid emergency status transition from {r.status}")
    r.status=target; setattr(r,stamp,datetime.utcnow())
    templates={EmergencyStatus.ON_THE_WAY:("SIREN_ON_THE_WAY","siren_on_the_way"),EmergencyStatus.ARRIVED:("SIREN_ARRIVED","siren_arrived"),EmergencyStatus.IN_SERVICE:("SIREN_SERVICE_STARTED","siren_service_started"),EmergencyStatus.RESOLVED:("SIREN_RESOLVED","siren_resolved")}
    notification_type,template_name=templates[target]
    NotificationService.from_template(db,r.user_id,notification_type,template_name,"SIREN",r.id,f"siren:{r.id}:{target.value}")
    db.commit(); return r
@provider_router.post("/requests/{request_id}/on-the-way",response_model=EmergencyRequestResponse)
def on_way(request_id,user=Depends(require_role(UserRole.EMERGENCY_PROVIDER)),db:Session=Depends(get_db)): return transition(request_id,user,EmergencyStatus.ON_THE_WAY,EmergencyStatus.ACCEPTED,"on_the_way_at",db)
@provider_router.post("/requests/{request_id}/arrived",response_model=EmergencyRequestResponse)
def arrived(request_id,user=Depends(require_role(UserRole.EMERGENCY_PROVIDER)),db:Session=Depends(get_db)): return transition(request_id,user,EmergencyStatus.ARRIVED,EmergencyStatus.ON_THE_WAY,"arrived_at",db)
@provider_router.post("/requests/{request_id}/service-started",response_model=EmergencyRequestResponse)
def service_started(request_id,user=Depends(require_role(UserRole.EMERGENCY_PROVIDER)),db:Session=Depends(get_db)): return transition(request_id,user,EmergencyStatus.IN_SERVICE,EmergencyStatus.ARRIVED,None,db)
@provider_router.post("/requests/{request_id}/resolve",response_model=EmergencyRequestResponse)
def resolve(request_id,user=Depends(require_role(UserRole.EMERGENCY_PROVIDER)),db:Session=Depends(get_db)):
    request = db.scalar(select(EmergencyRequest).where(EmergencyRequest.id == request_id))
    expected = EmergencyStatus.IN_SERVICE if request and request.status == EmergencyStatus.IN_SERVICE else EmergencyStatus.ARRIVED
    return transition(request_id,user,EmergencyStatus.RESOLVED,expected,"resolved_at",db)
@provider_router.post("/requests/{request_id}/cancel",response_model=EmergencyRequestResponse)
def cancel_provider_request(request_id:int,user=Depends(require_role(UserRole.EMERGENCY_PROVIDER)),db:Session=Depends(get_db)):
    p=provider_for(user,db); r=db.scalar(select(EmergencyRequest).where(EmergencyRequest.id==request_id,EmergencyRequest.provider_id==p.id).with_for_update())
    if not r: raise HTTPException(404,"Emergency request not found")
    if r.status not in {EmergencyStatus.ACCEPTED,EmergencyStatus.ON_THE_WAY}: raise HTTPException(400,"Request cannot be cancelled now")
    r.status=EmergencyStatus.CANCELLED; r.cancelled_at=datetime.utcnow()
    NotificationService.create_notification(db,r.user_id,"Siren request cancelled","Your provider cancelled this request.","SYSTEM","SIREN",r.id,f"siren:{r.id}:cancelled:provider")
    db.commit(); return r

@admin_router.get("/provider-applications",response_model=list[ProviderApplicationResponse])
def admin_apps(user:User=Depends(require_role(UserRole.ADMIN)),db:Session=Depends(get_db)): return db.scalars(select(ProviderApplication).order_by(ProviderApplication.created_at.desc())).all()
@admin_router.patch("/provider-applications/{application_id}",response_model=ProviderApplicationResponse)
def admin_decide(application_id:int,payload:AdminApplicationDecision,user:User=Depends(require_role(UserRole.ADMIN)),db:Session=Depends(get_db)):
    a=db.get(ProviderApplication,application_id)
    if not a or a.status!=ApplicationStatus.PENDING or payload.status not in {ApplicationStatus.APPROVED,ApplicationStatus.REJECTED}: raise HTTPException(400,"Invalid provider application decision")
    a.status=payload.status; a.admin_notes=payload.admin_notes
    if payload.status==ApplicationStatus.APPROVED:
        a.user.role=UserRole.EMERGENCY_PROVIDER
        db.add(EmergencyProvider(user_id=a.user_id,provider_type=a.provider_type,business_name=a.business_name,contact_name=a.contact_name,phone=a.phone,email=a.email,address=a.address,area=a.area,city=a.city,state=a.state,pincode=a.pincode,is_verified=True,is_active=True))
    db.commit(); db.refresh(a); return a
@admin_router.get("/emergency",response_model=list[EmergencyRequestResponse])
def admin_emergency(user:User=Depends(require_role(UserRole.ADMIN)),db:Session=Depends(get_db)): return db.scalars(select(EmergencyRequest).order_by(EmergencyRequest.created_at.desc())).all()
@admin_router.get("/providers")
def admin_providers(user:User=Depends(require_role(UserRole.ADMIN)),db:Session=Depends(get_db)): return db.execute(select(EmergencyProvider)).scalars().all()
@admin_router.patch("/providers/{provider_id}/status")
def admin_provider_status(provider_id:int,payload:dict,user:User=Depends(require_role(UserRole.ADMIN)),db:Session=Depends(get_db)):
    p=db.get(EmergencyProvider,provider_id)
    if not p: raise HTTPException(404,"Provider not found")
    if "is_verified" in payload:p.is_verified=bool(payload["is_verified"])
    if "is_active" in payload:p.is_active=bool(payload["is_active"])
    if not p.is_active:p.is_online=False
    db.commit(); return p
