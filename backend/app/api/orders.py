from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.cart import get_or_create_cart
from app.api.dependencies import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models import Address, CartItem, Coupon, CouponUsage, FoodItem, Order, OrderItem, OrderStatus, PaymentMethod, PaymentStatus, Product, Restaurant, User, UserEvent, Vendor
from app.schemas.commerce import OrderCreateRequest, OrderResponse
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/api/orders", tags=["orders"])


def order_query(order_id: int, user: User, db: Session):
    return db.scalar(select(Order).options(selectinload(Order.items), selectinload(Order.delivery)).where(Order.id == order_id, Order.user_id == user.id))


def next_order_number(db: Session) -> str:
    count = db.scalar(select(func.count(Order.id))) or 0
    return f"CHG{10001 + count:05d}"


@router.post("", response_model=OrderResponse, status_code=201)
def create_order(payload: OrderCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.payment_method not in {PaymentMethod.CASH_ON_DELIVERY, PaymentMethod.UPI_MANUAL}:
        raise HTTPException(status_code=400, detail="Unsupported payment method")
    address = db.scalar(select(Address).where(Address.id == payload.address_id, Address.user_id == user.id))
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    cart = get_or_create_cart(user, db)
    if not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    subtotal = Decimal("0")
    order_items = []
    restaurant_id = None
    seller_id = None
    try:
        for item in cart.items:
            if item.food_item_id:
                source = db.scalar(select(FoodItem).where(FoodItem.id == item.food_item_id).with_for_update())
                restaurant = db.get(Restaurant, source.restaurant_id) if source else None
                vendor = db.scalar(select(Vendor).where(Vendor.user_id == restaurant.owner_id)) if restaurant else None
                if not source or not source.is_available or not restaurant or not restaurant.is_active or (vendor and not vendor.is_active):
                    raise HTTPException(status_code=400, detail="Food item unavailable")
                restaurant_id = source.restaurant_id
            else:
                source = db.scalar(select(Product).where(Product.id == item.product_id).with_for_update())
                vendor = db.scalar(select(Vendor).where(Vendor.user_id == source.seller_id)) if source else None
                if not source or not source.is_available or (vendor and not vendor.is_active) or source.stock_quantity < item.quantity:
                    raise HTTPException(status_code=400, detail="Product unavailable")
                source.stock_quantity -= item.quantity
                seller_id = source.seller_id
            unit_price = source.price
            total_price = unit_price * item.quantity
            subtotal += total_price
            order_items.append(OrderItem(food_item_id=item.food_item_id, product_id=item.product_id, item_name=source.name, quantity=item.quantity, unit_price=unit_price, total_price=total_price))
        delivery_fee = Decimal(str(settings.delivery_fee))
        tax = subtotal * Decimal(str(settings.tax_rate))
        discount = Decimal("0")
        coupon = None
        if payload.coupon_code:
            coupon = db.scalar(select(Coupon).where(Coupon.code == payload.coupon_code.strip().upper(), Coupon.is_active.is_(True)))
            if not coupon or (coupon.expires_at and coupon.expires_at <= datetime.now(timezone.utc)):
                raise HTTPException(400, "Coupon is invalid or expired")
            if subtotal < coupon.minimum_order_amount:
                raise HTTPException(400, "Order does not meet the coupon minimum")
            if coupon.usage_limit is not None and (db.scalar(select(func.count(CouponUsage.id)).where(CouponUsage.coupon_id == coupon.id)) or 0) >= coupon.usage_limit:
                raise HTTPException(400, "Coupon usage limit reached")
            if (db.scalar(select(func.count(CouponUsage.id)).where(CouponUsage.coupon_id == coupon.id, CouponUsage.user_id == user.id)) or 0) >= coupon.per_user_limit:
                raise HTTPException(400, "Coupon usage limit reached for this user")
            discount = subtotal * coupon.discount_percent / Decimal("100") if coupon.discount_percent is not None else coupon.discount_amount or Decimal("0")
            if coupon.maximum_discount is not None: discount = min(discount, coupon.maximum_discount)
            discount = min(max(discount, Decimal("0")), subtotal + delivery_fee + tax)
        order = Order(order_number=next_order_number(db), user_id=user.id, restaurant_id=restaurant_id, seller_id=seller_id, status=OrderStatus.PENDING, subtotal=subtotal, delivery_fee=delivery_fee, tax=tax, discount=discount, total_amount=subtotal + delivery_fee + tax - discount, payment_method=payload.payment_method, payment_status=PaymentStatus.PENDING, delivery_address=f"{address.full_name}, {address.phone}, {address.address_line}, {address.area}, {address.city}, {address.state} - {address.pincode}", items=order_items)
        db.add(order)
        db.flush()
        if coupon: db.add(CouponUsage(coupon_id=coupon.id, user_id=user.id, order_id=order.id))
        NotificationService.from_template(db, user.id, "ORDER_CREATED", "order_created", "ORDER", order.id,
                                          f"order:{order.id}:created", order_number=order.order_number)
        vendor_user_id = order.seller_id
        if order.restaurant_id:
            vendor_user_id = db.scalar(select(Restaurant.owner_id).where(Restaurant.id == order.restaurant_id))
        if vendor_user_id:
            NotificationService.from_template(db, vendor_user_id, "NEW_VENDOR_ORDER", "vendor_order", "ORDER", order.id,
                                              f"order:{order.id}:vendor-created", order_number=order.order_number)
        for item in cart.items:
            db.add(UserEvent(user_id=user.id, event_type="PURCHASE", entity_type="FOOD" if item.food_item_id else "PRODUCT", entity_id=item.food_item_id or item.product_id))
        cart.items.clear()
        db.commit()
        db.refresh(order)
        return order_query(order.id, user, db)
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unable to create order") from None


@router.get("", response_model=list[OrderResponse])
def list_orders(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Order).options(selectinload(Order.items)).where(Order.user_id == user.id).order_by(Order.created_at.desc())).all()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = order_query(order_id, user, db)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = order_query(order_id, user, db)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status not in {OrderStatus.PENDING, OrderStatus.CONFIRMED}:
        raise HTTPException(status_code=400, detail="Order cannot be cancelled")
    order.status = OrderStatus.CANCELLED
    NotificationService.from_template(db, user.id, "ORDER_CANCELLED", "order_cancelled", "ORDER", order.id,
                                      f"order:{order.id}:cancelled:customer", order_number=order.order_number)
    vendor_user_id = order.seller_id
    if order.restaurant_id:
        vendor_user_id = db.scalar(select(Restaurant.owner_id).where(Restaurant.id == order.restaurant_id))
    if vendor_user_id:
        NotificationService.from_template(db, vendor_user_id, "ORDER_CANCELLED", "vendor_order_cancelled", "ORDER", order.id,
                                          f"order:{order.id}:cancelled:vendor", order_number=order.order_number)
    db.commit()
    return order_query(order.id, user, db)
