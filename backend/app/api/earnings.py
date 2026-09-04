from fastapi import APIRouter, Depends
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from app.api.dependencies import require_role
from app.db.session import get_db
from datetime import date, timedelta
from app.models import Delivery, DeliveryStatus, Driver, EarningRecord, EmergencyProvider, EmergencyRequest, EmergencyStatus, Order, OrderStatus, Restaurant, User, UserRole, Wallet, WalletTransaction

router = APIRouter(prefix="/api/earnings", tags=["earnings"])

@router.get("")
def earnings(user: User = Depends(require_role(UserRole.VENDOR, UserRole.DRIVER, UserRole.EMERGENCY_PROVIDER)), db: Session = Depends(get_db)):
    records = select(EarningRecord).where(EarningRecord.user_id == user.id)
    today = date.today().isoformat()
    week_start = date.today() - timedelta(days=6)
    total = db.scalar(select(func.coalesce(func.sum(EarningRecord.net_amount), 0)).where(EarningRecord.user_id == user.id)) or 0
    today_total = db.scalar(select(func.coalesce(func.sum(EarningRecord.net_amount), 0)).where(EarningRecord.user_id == user.id, func.date(EarningRecord.created_at) == today)) or 0
    week_total = db.scalar(select(func.coalesce(func.sum(EarningRecord.net_amount), 0)).where(EarningRecord.user_id == user.id, func.date(EarningRecord.created_at) >= week_start.isoformat())) or 0
    completed = db.scalar(select(func.count(EarningRecord.id)).where(EarningRecord.user_id == user.id)) or 0
    account = db.scalar(select(Wallet).where(Wallet.user_id == user.id))
    return {"role": user.role, "completed_items": completed, "gross": total, "earnings": total, "today_earnings": today_total, "weekly_earnings": week_total, "monthly_earnings": total, "pending_earnings": 0, "wallet_balance": account.balance if account else 0, "currency": "INR", "records": db.scalars(records.order_by(EarningRecord.created_at.desc()).limit(100)).all()}


@router.get("/wallet")
def wallet(user: User = Depends(require_role(UserRole.VENDOR, UserRole.DRIVER, UserRole.EMERGENCY_PROVIDER)), db: Session = Depends(get_db)):
    account = db.scalar(select(Wallet).where(Wallet.user_id == user.id))
    transactions = db.scalars(select(WalletTransaction).join(Wallet).where(Wallet.user_id == user.id).order_by(WalletTransaction.created_at.desc()).limit(100)).all()
    return {"balance": account.balance if account else 0, "transactions": transactions, "currency": "INR"}