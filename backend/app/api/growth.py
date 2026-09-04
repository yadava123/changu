from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import LoyaltyAccount, LoyaltyTransaction, Referral, User

router = APIRouter(tags=["growth"])

class ReferralCodeRequest(BaseModel): code: str = Field(min_length=3, max_length=40)

@router.get("/api/loyalty")
def loyalty(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    account = db.scalar(select(LoyaltyAccount).where(LoyaltyAccount.user_id == user.id))
    transactions = db.scalars(select(LoyaltyTransaction).where(LoyaltyTransaction.user_id == user.id).order_by(LoyaltyTransaction.created_at.desc()).limit(100)).all()
    return {"points": account.points if account else 0, "transactions": transactions}

@router.get("/api/referrals")
def referrals(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    code = db.scalar(select(Referral).where(Referral.referrer_id == user.id))
    if not code:
        code = Referral(code=f"CHGREF{user.id:06d}", referrer_id=user.id)
        db.add(code); db.commit(); db.refresh(code)
    sent = db.scalars(select(Referral).where(Referral.referrer_id == user.id, Referral.referred_id.is_not(None))).all()
    return {"code": code.code, "referrals": sent}

@router.post("/api/referrals/apply")
def apply_referral(payload: ReferralCodeRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    code = db.scalar(select(Referral).where(Referral.code == payload.code.strip().upper()))
    if not code: raise HTTPException(404, "Referral code not found")
    if code.referrer_id == user.id: raise HTTPException(400, "You cannot use your own referral code")
    if db.scalar(select(Referral).where(Referral.referred_id == user.id)): raise HTTPException(409, "A referral is already associated with this account")
    if code.referred_id is not None: raise HTTPException(409, "This referral code has already been used")
    code.referred_id = user.id
    try: db.commit()
    except IntegrityError: db.rollback(); raise HTTPException(409, "Referral code is no longer available") from None
    return {"status": "applied"}