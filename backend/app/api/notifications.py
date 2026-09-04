from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import Notification, User

router=APIRouter(prefix="/api/notifications",tags=["notifications"])
@router.get("")
def notifications(page:int=1,limit:int=20,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    limit=min(max(limit,1),100); total=db.scalar(select(func.count(Notification.id)).where(Notification.user_id==user.id)) or 0; items=db.scalars(select(Notification).where(Notification.user_id==user.id).order_by(Notification.created_at.desc()).offset((max(page,1)-1)*limit).limit(limit)).all(); return {"items":items,"page":max(page,1),"limit":limit,"total":total,"pages":(total+limit-1)//limit}
@router.get("/unread-count")
def unread_count(user:User=Depends(get_current_user),db:Session=Depends(get_db)): return {"count":db.scalar(select(func.count(Notification.id)).where(Notification.user_id==user.id,Notification.is_read.is_(False))) or 0}
@router.patch("/{notification_id}/read")
def read(notification_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    item=db.scalar(select(Notification).where(Notification.id==notification_id,Notification.user_id==user.id))
    if not item: raise HTTPException(404,"Notification not found")
    item.is_read=True; item.read_at=datetime.now(timezone.utc); db.commit(); return item
@router.patch("/read-all")
def read_all(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    for item in db.scalars(select(Notification).where(Notification.user_id==user.id,Notification.is_read.is_(False))).all(): item.is_read=True; item.read_at=datetime.now(timezone.utc)
    db.commit(); return {"status":"ok"}
@router.delete("/{notification_id}",status_code=204)
def delete(notification_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    item=db.scalar(select(Notification).where(Notification.id==notification_id,Notification.user_id==user.id))
    if not item: raise HTTPException(404,"Notification not found")
    db.delete(item); db.commit()
