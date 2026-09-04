from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import NotificationPreference, User
router=APIRouter(prefix="/api/notification-preferences",tags=["notifications"])
class PreferenceUpdate(BaseModel): order_updates:bool=True; delivery_updates:bool=True; payment_updates:bool=True; promotions:bool=True; loyalty:bool=True; referrals:bool=True; system_notifications:bool=True
def get_pref(user,db):
    p=db.scalar(select(NotificationPreference).where(NotificationPreference.user_id==user.id))
    if not p:p=NotificationPreference(user_id=user.id);db.add(p);db.flush()
    return p
@router.get("")
def get(user:User=Depends(get_current_user),db:Session=Depends(get_db)): return get_pref(user,db)
@router.patch("")
def update(payload:PreferenceUpdate,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    p=get_pref(user,db)
    for k,v in payload.model_dump().items():setattr(p,k,v)
    db.commit();db.refresh(p);return p
