from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.restaurant import Restaurant
from app.models.vendor import Vendor
from app.schemas.restaurant import RestaurantResponse

router = APIRouter(prefix="/api/restaurants", tags=["restaurants"])


@router.get("", response_model=list[RestaurantResponse])
def list_restaurants(city: str | None = None, is_active: bool = True, db: Session = Depends(get_db)):
    statement = select(Restaurant).outerjoin(Vendor, Vendor.user_id == Restaurant.owner_id).where(Restaurant.is_active == is_active, or_(Vendor.id.is_(None), Vendor.is_active.is_(True))).order_by(Restaurant.name)
    if city:
        statement = statement.where(Restaurant.city.ilike(city))
    return db.scalars(statement).all()


@router.get("/{restaurant_id}", response_model=RestaurantResponse)
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.get(Restaurant, restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    return restaurant
