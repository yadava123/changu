from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import LoyaltyAccount, LoyaltyTransaction

def award_order_points(db: Session, user_id: int, order_id: int, total_amount: Decimal):
    event_key = f"order:{order_id}:delivered"
    if db.scalar(select(LoyaltyTransaction).where(LoyaltyTransaction.user_id == user_id, LoyaltyTransaction.event_key == event_key)):
        return None
    account = db.scalar(select(LoyaltyAccount).where(LoyaltyAccount.user_id == user_id))
    if not account:
        account = LoyaltyAccount(user_id=user_id, points=0); db.add(account); db.flush()
    points = max(0, int(total_amount // Decimal("10")))
    account.points += points
    transaction = LoyaltyTransaction(user_id=user_id, points=points, event_key=event_key, description=f"Order {order_id} delivered")
    db.add(transaction)
    db.flush()
    return transaction