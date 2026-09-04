from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from app.api.dependencies import require_role
from app.db.session import get_db
from app.models import AuditLog, Coupon, Delivery, DeliveryStatus, Driver, EarningRecord, EmergencyProvider, EmergencyRequest, EmergencyStatus, FoodItem, Notification, Order, OrderStatus, Parcel, ParcelStatus, PaymentTransaction, PaymentTransactionStatus, PlatformSetting, Product, Ride, RideStatus, User, UserRole, Vendor

router=APIRouter(prefix="/api/admin",tags=["admin control"]); admin_only=require_role(UserRole.ADMIN)
class StatusUpdate(BaseModel): is_active:bool
class SettingUpdate(BaseModel): value:str=Field(min_length=1,max_length=255)
class NotificationRequest(BaseModel): title:str=Field(min_length=1); message:str=Field(min_length=1); target:str
class CancelRequest(BaseModel): reason:str=Field(min_length=3,max_length=1000)
class CouponCreate(BaseModel):
    code:str=Field(min_length=3,max_length=40); discount_percent:float|None=Field(default=None,gt=0,le=100); discount_amount:float|None=Field(default=None,gt=0); minimum_order_amount:float=Field(default=0,ge=0); maximum_discount:float|None=Field(default=None,gt=0); usage_limit:int|None=Field(default=None,gt=0); per_user_limit:int=Field(default=1,gt=0); expires_at:datetime|None=None
    def model_post_init(self,__context):
        if (self.discount_percent is None)==(self.discount_amount is None): raise ValueError('Provide exactly one discount type')
def audit(db,admin,action,entity,entity_id,old=None,new=None,reason=None):db.add(AuditLog(admin_user_id=admin.id,action=action,entity_type=entity,entity_id=entity_id,old_value=old,new_value=new,reason=reason))
def page_args(page,limit):return max(page,1),min(max(limit,1),100)
@router.get('/dashboard')
def dashboard(user:User=Depends(admin_only),db:Session=Depends(get_db)):
    today=date.today().isoformat(); active_orders=[OrderStatus.PENDING,OrderStatus.CONFIRMED,OrderStatus.PREPARING,OrderStatus.READY_FOR_PICKUP,OrderStatus.DRIVER_ASSIGNED,OrderStatus.OUT_FOR_DELIVERY]
    active_parcels=[ParcelStatus.PENDING,ParcelStatus.ACCEPTED,ParcelStatus.PICKED_UP,ParcelStatus.IN_TRANSIT,ParcelStatus.OUT_FOR_DELIVERY]
    active_rides=[RideStatus.REQUESTED,RideStatus.DRIVER_ASSIGNED,RideStatus.DRIVER_ARRIVING,RideStatus.DRIVER_ARRIVED,RideStatus.RIDE_STARTED]
    active_siren=[EmergencyStatus.CREATED,EmergencyStatus.SEARCHING,EmergencyStatus.PROVIDER_ASSIGNED,EmergencyStatus.ACCEPTED,EmergencyStatus.ON_THE_WAY,EmergencyStatus.ARRIVED,EmergencyStatus.IN_SERVICE]
    return {'total_users':db.query(User).count(),'total_customers':db.query(User).filter(User.role==UserRole.CUSTOMER).count(),'total_vendors':db.query(Vendor).count(),'active_vendors':db.query(Vendor).filter(Vendor.is_active.is_(True)).count(),'total_drivers':db.query(Driver).count(),'online_drivers':db.query(Driver).filter(Driver.is_online.is_(True)).count(),'total_providers':db.query(EmergencyProvider).count(),'orders_today':db.query(Order).filter(func.date(Order.created_at)==today).count(),'total_orders':db.query(Order).count(),'active_orders':db.query(Order).filter(Order.status.in_(active_orders)).count(),'completed_orders':db.query(Order).filter(Order.status==OrderStatus.DELIVERED).count(),'revenue_today':db.query(func.coalesce(func.sum(Order.total_amount),0)).filter(func.date(Order.created_at)==today,Order.status!=OrderStatus.CANCELLED).scalar(),'pending_orders':db.query(Order).filter(Order.status==OrderStatus.PENDING).count(),'active_deliveries':db.query(Delivery).filter(Delivery.status.in_([DeliveryStatus.AVAILABLE,DeliveryStatus.ASSIGNED,DeliveryStatus.ACCEPTED,DeliveryStatus.PICKED_UP,DeliveryStatus.OUT_FOR_DELIVERY])).count(),'total_parcels':db.query(Parcel).count(),'active_parcels':db.query(Parcel).filter(Parcel.status.in_(active_parcels)).count(),'delivered_parcels':db.query(Parcel).filter(Parcel.status==ParcelStatus.DELIVERED).count(),'total_rides':db.query(Ride).count(),'active_rides':db.query(Ride).filter(Ride.status.in_(active_rides)).count(),'completed_rides':db.query(Ride).filter(Ride.status==RideStatus.RIDE_COMPLETED).count(),'active_siren_requests':db.query(EmergencyRequest).filter(EmergencyRequest.status.in_(active_siren)).count(),'total_siren_requests':db.query(EmergencyRequest).count(),'resolved_siren_requests':db.query(EmergencyRequest).filter(EmergencyRequest.status==EmergencyStatus.RESOLVED).count(),'ai_requests_today':db.query(func.coalesce(func.sum(__import__('app.models',fromlist=['AIUsage']).AIUsage.request_count),0)).filter(func.date(__import__('app.models',fromlist=['AIUsage']).AIUsage.created_at)==today).scalar()}
@router.get('/financial-summary')
def financial_summary(user:User=Depends(admin_only),db:Session=Depends(get_db)):
    today=date.today().isoformat()
    return {'total_revenue': db.scalar(select(func.coalesce(func.sum(PaymentTransaction.amount),0)).where(PaymentTransaction.status==PaymentTransactionStatus.SUCCESS)) or 0, 'revenue_today': db.scalar(select(func.coalesce(func.sum(PaymentTransaction.amount),0)).where(PaymentTransaction.status==PaymentTransactionStatus.SUCCESS,func.date(PaymentTransaction.created_at)==today)) or 0, 'successful_payments': db.scalar(select(func.count(PaymentTransaction.id)).where(PaymentTransaction.status==PaymentTransactionStatus.SUCCESS)) or 0, 'failed_payments': db.scalar(select(func.count(PaymentTransaction.id)).where(PaymentTransaction.status==PaymentTransactionStatus.FAILED)) or 0, 'refunded_payments': db.scalar(select(func.count(PaymentTransaction.id)).where(PaymentTransaction.status==PaymentTransactionStatus.REFUNDED)) or 0, 'total_commission': db.scalar(select(func.coalesce(func.sum(EarningRecord.commission_amount),0))) or 0, 'total_earnings': db.scalar(select(func.coalesce(func.sum(EarningRecord.net_amount),0))) or 0}
@router.get('/financial-transactions')
def financial_transactions(transaction_id:str|None=None,status:PaymentTransactionStatus|None=None,role:UserRole|None=None,page:int=1,limit:int=20,user:User=Depends(admin_only),db:Session=Depends(get_db)):
    page,limit=page_args(page,limit); q=select(PaymentTransaction).join(User,User.id==PaymentTransaction.user_id).order_by(PaymentTransaction.created_at.desc())
    if transaction_id:q=q.where(PaymentTransaction.transaction_id.ilike(f'%{transaction_id}%'))
    if status:q=q.where(PaymentTransaction.status==status)
    if role:q=q.where(User.role==role)
    return {'items':db.scalars(q.offset((page-1)*limit).limit(limit)).all(),'page':page,'limit':limit}
@router.get('/users')
def users(search:str|None=None,role:UserRole|None=None,page:int=1,limit:int=20,user:User=Depends(admin_only),db:Session=Depends(get_db)):
    page,limit=page_args(page,limit); q=select(User).order_by(User.created_at.desc()); count=select(func.count(User.id))
    if search: condition=or_(User.full_name.ilike(f'%{search}%'),User.email.ilike(f'%{search}%'));q=q.where(condition);count=count.where(condition)
    if role:q=q.where(User.role==role);count=count.where(User.role==role)
    total=db.scalar(count) or 0;items=db.scalars(q.offset((page-1)*limit).limit(limit)).all();return {'items':[{'id':x.id,'full_name':x.full_name,'email':x.email,'role':x.role,'is_active':x.is_active,'created_at':x.created_at} for x in items],'total':total,'page':page,'limit':limit}
@router.get('/users/{user_id}')
def user_detail(user_id:int,user:User=Depends(admin_only),db:Session=Depends(get_db)):
    item=db.get(User,user_id)
    if not item:raise HTTPException(404,'User not found')
    return {'id':item.id,'full_name':item.full_name,'email':item.email,'role':item.role,'is_active':item.is_active,'created_at':item.created_at,'order_count':db.query(Order).filter(Order.user_id==item.id).count()}
@router.patch('/users/{user_id}/status')
def user_status(user_id:int,payload:StatusUpdate,user:User=Depends(admin_only),db:Session=Depends(get_db)):
    item=db.get(User,user_id)
    if not item:raise HTTPException(404,'User not found')
    old=str(item.is_active);item.is_active=payload.is_active;audit(db,user,'USER_ACTIVATED' if payload.is_active else 'USER_SUSPENDED','USER',item.id,old,str(payload.is_active));db.commit();return {'is_active':item.is_active}
@router.get('/vendors')
def vendors(page:int=1,limit:int=20,user:User=Depends(admin_only),db:Session=Depends(get_db)):
    page,limit=page_args(page,limit);total=db.query(Vendor).count();items=db.scalars(select(Vendor).order_by(Vendor.created_at.desc()).offset((page-1)*limit).limit(limit)).all();return {'items':items,'total':total,'page':page,'limit':limit}
@router.patch('/vendors/{vendor_id}/status')
def vendor_status(vendor_id:int,payload:StatusUpdate,user:User=Depends(admin_only),db:Session=Depends(get_db)):
    item=db.get(Vendor,vendor_id)
    if not item:raise HTTPException(404,'Vendor not found')
    old=str(item.is_active);item.is_active=payload.is_active;audit(db,user,'VENDOR_ACTIVATED' if payload.is_active else 'VENDOR_DEACTIVATED','VENDOR',vendor_id,old,str(payload.is_active));db.commit();return item
@router.get('/products')
def products(page:int=1,limit:int=20,user:User=Depends(admin_only),db:Session=Depends(get_db)):
    page,limit=page_args(page,limit);return {'items':db.scalars(select(Product).offset((page-1)*limit).limit(limit)).all(),'total':db.query(Product).count(),'page':page,'limit':limit}
@router.patch('/products/{product_id}/status')
def product_status(product_id:int,payload:StatusUpdate,user:User=Depends(admin_only),db:Session=Depends(get_db)):
    item=db.get(Product,product_id)
    if not item:raise HTTPException(404,'Product not found')
    item.is_available=payload.is_active;audit(db,user,'PRODUCT_ENABLED' if payload.is_active else 'PRODUCT_DISABLED','PRODUCT',product_id);db.commit();return item
@router.get('/orders')
def orders(status:OrderStatus|None=None,page:int=1,limit:int=20,user:User=Depends(admin_only),db:Session=Depends(get_db)):
    page,limit=page_args(page,limit);q=select(Order).order_by(Order.created_at.desc());count=select(func.count(Order.id))
    if status:q=q.where(Order.status==status);count=count.where(Order.status==status)
    return {'items':db.scalars(q.offset((page-1)*limit).limit(limit)).all(),'total':db.scalar(count) or 0,'page':page,'limit':limit}
@router.post('/orders/{order_id}/cancel')
def cancel_order(order_id:int,payload:CancelRequest,user:User=Depends(admin_only),db:Session=Depends(get_db)):
    item=db.get(Order,order_id)
    if not item:raise HTTPException(404,'Order not found')
    if item.status in {OrderStatus.DELIVERED,OrderStatus.CANCELLED}:raise HTTPException(400,'Order cannot be cancelled')
    old=item.status.value;item.status=OrderStatus.CANCELLED;audit(db,user,'ORDER_CANCELLED','ORDER',order_id,old,'CANCELLED',payload.reason);db.commit();return item
@router.get('/deliveries')
def deliveries(status:DeliveryStatus|None=None,user:User=Depends(admin_only),db:Session=Depends(get_db)):
    q=select(Delivery).order_by(Delivery.created_at.desc())
    if status:q=q.where(Delivery.status==status)
    return db.scalars(q).all()
@router.get('/parcels')
def parcels(status:ParcelStatus|None=None,search:str|None=None,page:int=1,limit:int=20,user:User=Depends(admin_only),db:Session=Depends(get_db)):
    page,limit=page_args(page,limit); q=select(Parcel).order_by(Parcel.created_at.desc()); count=select(func.count(Parcel.id))
    if status:q=q.where(Parcel.status==status); count=count.where(Parcel.status==status)
    if search and search.isdigit():q=q.where(Parcel.id==int(search)); count=count.where(Parcel.id==int(search))
    return {'items':db.scalars(q.offset((page-1)*limit).limit(limit)).all(),'total':db.scalar(count) or 0,'page':page,'limit':limit}
@router.get('/rides')
def rides(status:RideStatus|None=None,search:str|None=None,page:int=1,limit:int=20,user:User=Depends(admin_only),db:Session=Depends(get_db)):
    page,limit=page_args(page,limit); q=select(Ride).order_by(Ride.created_at.desc()); count=select(func.count(Ride.id))
    if status:q=q.where(Ride.status==status); count=count.where(Ride.status==status)
    if search and search.isdigit():q=q.where(Ride.id==int(search)); count=count.where(Ride.id==int(search))
    return {'items':db.scalars(q.offset((page-1)*limit).limit(limit)).all(),'total':db.scalar(count) or 0,'page':page,'limit':limit}
@router.get('/siren')
def siren(status:EmergencyStatus|None=None,search:str|None=None,page:int=1,limit:int=20,user:User=Depends(admin_only),db:Session=Depends(get_db)):
    page,limit=page_args(page,limit); q=select(EmergencyRequest).order_by(EmergencyRequest.created_at.desc()); count=select(func.count(EmergencyRequest.id))
    if status:q=q.where(EmergencyRequest.status==status); count=count.where(EmergencyRequest.status==status)
    if search and search.isdigit():q=q.where(EmergencyRequest.id==int(search)); count=count.where(EmergencyRequest.id==int(search))
    return {'items':db.scalars(q.offset((page-1)*limit).limit(limit)).all(),'total':db.scalar(count) or 0,'page':page,'limit':limit}
@router.get('/audit-logs')
def audit_logs(page:int=1,limit:int=20,user:User=Depends(admin_only),db:Session=Depends(get_db)):
    page,limit=page_args(page,limit);return {'items':db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).offset((page-1)*limit).limit(limit)).all(),'total':db.query(AuditLog).count(),'page':page,'limit':limit}
@router.get('/settings')
def settings(user:User=Depends(admin_only),db:Session=Depends(get_db)):return db.scalars(select(PlatformSetting).order_by(PlatformSetting.key)).all()
@router.patch('/settings/{key}')
def update_setting(key:str,payload:SettingUpdate,user:User=Depends(admin_only),db:Session=Depends(get_db)):
    allowed={'delivery_fee','tax_rate','ai_daily_limit','recommendation_enabled','siren_enabled','vendor_registration_enabled','driver_registration_enabled','provider_registration_enabled'}
    if key not in allowed:raise HTTPException(400,'Setting cannot be modified')
    item=db.scalar(select(PlatformSetting).where(PlatformSetting.key==key))
    if not item:item=PlatformSetting(key=key,description='Operational setting',value=payload.value);db.add(item)
    else:item.value=payload.value
    item.updated_by=user.id;audit(db,user,'SETTING_CHANGED','SETTING',item.id,None,payload.value);db.commit();return item
@router.post('/notifications')
def notify(payload:NotificationRequest,user:User=Depends(admin_only),db:Session=Depends(get_db)):
    q=select(User)
    if payload.target=='CUSTOMERS':q=q.where(User.role==UserRole.CUSTOMER)
    elif payload.target=='VENDORS':q=q.where(User.role==UserRole.VENDOR)
    elif payload.target=='DRIVERS':q=q.where(User.role==UserRole.DRIVER)
    elif payload.target=='PROVIDERS':q=q.where(User.role==UserRole.EMERGENCY_PROVIDER)
    recipients=db.scalars(q).all();db.add_all([Notification(user_id=r.id,title=payload.title,message=payload.message,type='SYSTEM') for r in recipients]);audit(db,user,'NOTIFICATION_SENT','PLATFORM',None,None,payload.target);db.commit();return {'recipients':len(recipients)}
@router.post('/coupons',status_code=201)
def create_coupon(payload:CouponCreate,user:User=Depends(admin_only),db:Session=Depends(get_db)):
    code=payload.code.strip().upper()
    if db.scalar(select(Coupon).where(Coupon.code==code)): raise HTTPException(409,'Coupon code already exists')
    coupon=Coupon(code=code,discount_percent=payload.discount_percent,discount_amount=payload.discount_amount,minimum_order_amount=payload.minimum_order_amount,maximum_discount=payload.maximum_discount,usage_limit=payload.usage_limit,per_user_limit=payload.per_user_limit,expires_at=payload.expires_at)
    db.add(coupon); audit(db,user,'COUPON_CREATED','COUPON',None,None,code); db.commit(); db.refresh(coupon); return coupon
