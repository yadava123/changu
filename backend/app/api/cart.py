from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models import Cart, CartItem, FoodItem, Product, Restaurant, User, UserEvent, Vendor
from app.schemas.commerce import CartItemRequest, CartItemResponse, CartItemUpdate, CartResponse

router = APIRouter(prefix="/api/cart", tags=["cart"])


def get_or_create_cart(user: User, db: Session) -> Cart:
    cart = db.scalar(select(Cart).where(Cart.user_id == user.id))
    if not cart:
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.flush()
    return cart


def item_source(item: CartItem):
    if item.food_item:
        return item.food_item.restaurant_id, None
    if item.product:
        return None, item.product.seller_id
    return None, None


def current_source(food: FoodItem | None, product: Product | None):
    return (food.restaurant_id, None) if food else (None, product.seller_id)


def cart_response(cart: Cart) -> CartResponse:
    items = []
    subtotal = Decimal("0")
    for item in cart.items:
        name = item.food_item.name if item.food_item else item.product.name
        image_url = item.food_item.image_url if item.food_item else item.product.image_url
        item_type = "FOOD" if item.food_item else "PRODUCT"
        total_price = item.unit_price * item.quantity
        subtotal += total_price
        items.append(CartItemResponse(id=item.id, name=name, quantity=item.quantity, unit_price=item.unit_price, total_price=total_price, image_url=image_url, type=item_type, food_item_id=item.food_item_id, product_id=item.product_id))
    delivery = Decimal(str(settings.delivery_fee)) if items else Decimal("0")
    tax = subtotal * Decimal(str(settings.tax_rate))
    return CartResponse(cart_id=cart.id, items=items, subtotal=subtotal, delivery_fee=delivery, tax=tax, discount=Decimal("0"), total=subtotal + delivery + tax)


@router.get("", response_model=CartResponse)
def get_cart(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = get_or_create_cart(user, db)
    db.commit()
    return cart_response(cart)


@router.post("/items", response_model=CartResponse)
def add_item(payload: CartItemRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = get_or_create_cart(user, db)
    food = db.get(FoodItem, payload.food_item_id) if payload.food_item_id else None
    product = db.get(Product, payload.product_id) if payload.product_id else None
    source = food or product
    if not source or not source.is_available or (product and product.stock_quantity < payload.quantity):
        raise HTTPException(status_code=400, detail="Item unavailable")
    if food:
        restaurant = db.get(Restaurant, food.restaurant_id)
        vendor = db.scalar(select(Vendor).where(Vendor.user_id == restaurant.owner_id)) if restaurant else None
        if not restaurant or not restaurant.is_active or (vendor and not vendor.is_active):
            raise HTTPException(status_code=400, detail="Store is not accepting orders")
    elif product:
        vendor = db.scalar(select(Vendor).where(Vendor.user_id == product.seller_id))
        if vendor and not vendor.is_active:
            raise HTTPException(status_code=400, detail="Store is not accepting orders")
    requested_source = current_source(food, product)
    for existing in cart.items:
        existing_source = item_source(existing)
        if existing_source != requested_source:
            raise HTTPException(status_code=409, detail="Your cart contains items from another store. Clear the existing cart before adding this item.")
    existing = next((item for item in cart.items if item.food_item_id == payload.food_item_id and item.product_id == payload.product_id), None)
    if existing:
        existing.quantity += payload.quantity
    else:
        cart.items.append(CartItem(food_item_id=payload.food_item_id, product_id=payload.product_id, quantity=payload.quantity, unit_price=source.price))
    db.add(UserEvent(user_id=user.id, event_type="ADD_TO_CART", entity_type="FOOD" if payload.food_item_id else "PRODUCT", entity_id=payload.food_item_id or payload.product_id))
    db.commit()
    db.refresh(cart)
    return cart_response(cart)


@router.patch("/items/{item_id}", response_model=CartResponse)
def update_item(item_id: int, payload: CartItemUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = get_or_create_cart(user, db)
    item = next((entry for entry in cart.items if entry.id == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    item.quantity = payload.quantity
    db.commit()
    return cart_response(cart)


@router.delete("/items/{item_id}", response_model=CartResponse)
def remove_item(item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = get_or_create_cart(user, db)
    item = next((entry for entry in cart.items if entry.id == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(item)
    db.commit()
    db.refresh(cart)
    return cart_response(cart)


@router.delete("", response_model=CartResponse)
def clear_cart(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = get_or_create_cart(user, db)
    cart.items.clear()
    db.commit()
    return cart_response(cart)
