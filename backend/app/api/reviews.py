from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import Order, OrderStatus, Review, User
from app.schemas.review import ReviewCreate, ReviewResponse

router = APIRouter(prefix="/api/reviews", tags=["reviews"])

@router.post("/orders/{order_id}", response_model=ReviewResponse, status_code=201)
def create_review(order_id: int, payload: ReviewCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.scalar(select(Order).where(Order.id == order_id, Order.user_id == user.id))
    if not order: raise HTTPException(404, "Order not found")
    if order.status != OrderStatus.DELIVERED: raise HTTPException(400, "Reviews are available after delivery")
    review = Review(user_id=user.id, order_id=order.id, rating=payload.rating, comment=payload.comment.strip())
    db.add(review)
    try: db.commit()
    except IntegrityError: db.rollback(); raise HTTPException(409, "You have already reviewed this order") from None
    db.refresh(review)
    return review

@router.get("/orders/{order_id}", response_model=ReviewResponse)
def get_review(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    review = db.scalar(select(Review).where(Review.order_id == order_id, Review.user_id == user.id))
    if not review: raise HTTPException(404, "Review not found")
    return review