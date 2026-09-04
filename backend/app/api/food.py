from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.food import FoodItem
from app.models.restaurant import Restaurant
from app.models.vendor import Vendor
from app.schemas.food import FoodItemResponse

router = APIRouter(prefix="/api/food", tags=["food"])


@router.get("", response_model=list[FoodItemResponse])
def list_food(
    restaurant_id: int | None = None,
    category: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    statement = select(FoodItem).join(Restaurant, Restaurant.id == FoodItem.restaurant_id).outerjoin(Vendor, Vendor.user_id == Restaurant.owner_id).where(FoodItem.is_available.is_(True), Restaurant.is_active.is_(True), or_(Vendor.id.is_(None), Vendor.is_active.is_(True))).order_by(FoodItem.name)
    if restaurant_id:
        statement = statement.where(FoodItem.restaurant_id == restaurant_id)
    if category:
        statement = statement.where(FoodItem.category.ilike(category))
    if search:
        term = f"%{search}%"
        statement = statement.where(or_(FoodItem.name.ilike(term), FoodItem.description.ilike(term)))
    return db.scalars(statement).all()


@router.get("/{food_id}", response_model=FoodItemResponse)
def get_food(food_id: int, db: Session = Depends(get_db)):
    food = db.get(FoodItem, food_id)
    if food is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found")
    return food
