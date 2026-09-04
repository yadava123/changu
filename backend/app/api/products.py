from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.product import Product
from app.models.vendor import Vendor
from app.schemas.product import ProductResponse

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=list[ProductResponse])
def list_products(
    category: str | None = None,
    search: str | None = None,
    seller_id: int | None = None,
    db: Session = Depends(get_db),
):
    statement = select(Product).outerjoin(Vendor, Vendor.user_id == Product.seller_id).where(Product.is_available.is_(True), or_(Vendor.id.is_(None), Vendor.is_active.is_(True))).order_by(Product.name)
    if category:
        statement = statement.where(Product.category.ilike(category))
    if search:
        term = f"%{search}%"
        statement = statement.where(or_(Product.name.ilike(term), Product.description.ilike(term)))
    if seller_id:
        statement = statement.where(Product.seller_id == seller_id)
    return db.scalars(statement).all()


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product
