from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.food import FoodItem
from app.models.product import Product
from app.models.restaurant import Restaurant
from app.schemas.food import FoodItemResponse
from app.schemas.product import ProductResponse
from app.schemas.restaurant import RestaurantResponse

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("")
def search(q: str = "", type: str | None = None, city: str | None = None, db: Session = Depends(get_db)):
    term = f"%{q.strip()}%"
    restaurants = []
    food = []
    products = []
    if not type or type in {"restaurant", "restaurants", "store", "stores"}:
        statement = select(Restaurant).where(Restaurant.is_active.is_(True), or_(Restaurant.name.ilike(term), Restaurant.description.ilike(term)))
        if city:
            statement = statement.where(Restaurant.city.ilike(city))
        restaurants = [RestaurantResponse.model_validate(item) for item in db.scalars(statement).all()]
    if not type or type in {"food", "restaurant", "restaurants"}:
        statement = select(FoodItem).where(FoodItem.is_available.is_(True), or_(FoodItem.name.ilike(term), FoodItem.description.ilike(term), FoodItem.category.ilike(term)))
        food = [FoodItemResponse.model_validate(item) for item in db.scalars(statement).all()]
    if not type or type in {"product", "products", "store", "stores"}:
        statement = select(Product).where(Product.is_available.is_(True), or_(Product.name.ilike(term), Product.description.ilike(term), Product.category.ilike(term)))
        products = [ProductResponse.model_validate(item) for item in db.scalars(statement).all()]
    return {"restaurants": restaurants, "food": food, "products": products}
