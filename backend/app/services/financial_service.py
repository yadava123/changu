from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import EarningRecord, EarningStatus, User, Wallet, WalletTransaction


def settle_earning(db: Session, user: User, source_type: str, source_id: int, gross_amount: Decimal | int, commission_amount: Decimal | int = 0) -> EarningRecord:
    existing = db.scalar(select(EarningRecord).where(EarningRecord.user_id == user.id, EarningRecord.source_type == source_type, EarningRecord.source_id == source_id))
    if existing:
        return existing
    gross = Decimal(str(gross_amount)).quantize(Decimal("0.01"))
    commission = Decimal(str(commission_amount)).quantize(Decimal("0.01"))
    net = gross - commission
    if net < 0:
        raise ValueError("Earning commission cannot exceed gross amount")
    earning = EarningRecord(user_id=user.id, source_type=source_type, source_id=source_id, gross_amount=gross, commission_amount=commission, net_amount=net, status=EarningStatus.AVAILABLE)
    db.add(earning)
    db.flush()
    wallet = db.scalar(select(Wallet).where(Wallet.user_id == user.id).with_for_update())
    if not wallet:
        wallet = Wallet(user_id=user.id, balance=Decimal("0.00"))
        db.add(wallet)
        db.flush()
    wallet.balance += net
    db.add(WalletTransaction(wallet_id=wallet.id, amount=net, transaction_type="WALLET_CREDIT", idempotency_key=f"earning:{source_type}:{source_id}:{user.id}", reference_type=source_type, reference_id=source_id))
    return earning