from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.models import Order, OrderStatus, Parcel, ParcelStatus, PaymentServiceType, PaymentStatus, PaymentTransaction, PaymentTransactionStatus, Ride, RideStatus, User, UserRole
from app.services.notification_service import NotificationService
from app.core.config import settings
from app.core.rate_limit import enforce_rate_limit

router = APIRouter(prefix="/api/payments", tags=["payments"])


def own_order(order_id: int, user: User, db: Session) -> Order:
    order = db.scalar(select(Order).where(Order.id == order_id, Order.user_id == user.id))
    if not order:
        raise HTTPException(404, "Order not found")
    return order


def record(db: Session, order: Order | None, status: PaymentTransactionStatus, amount=None, service_type=PaymentServiceType.ORDER, service_id=None, user_id=None):
    transaction = PaymentTransaction(transaction_id=f"CHGPAY-{uuid4().hex[:24].upper()}", order_id=order.id if order else None, user_id=user_id or order.user_id, amount=amount if amount is not None else order.total_amount, status=status, service_type=service_type, service_id=service_id)
    db.add(transaction)
    return transaction


@router.get("")
def transactions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(PaymentTransaction).where(PaymentTransaction.user_id == user.id).order_by(PaymentTransaction.created_at.desc())).all()


@router.post("/orders/{order_id}/success")
def payment_success(order_id: int, request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if settings.rate_limit_enabled: enforce_rate_limit(request, f"payment:order:{user.id}", 20)
    order = db.scalar(select(Order).where(Order.id == order_id, Order.user_id == user.id).with_for_update())
    if not order:
        raise HTTPException(404, "Order not found")
    if order.payment_status == PaymentStatus.PAID:
        existing = db.scalar(select(PaymentTransaction).where(PaymentTransaction.order_id == order.id, PaymentTransaction.status == PaymentTransactionStatus.SUCCESS))
        return {"status": "PAID", "transaction_id": existing.transaction_id if existing else None}
    if order.payment_status != PaymentStatus.PENDING:
        raise HTTPException(400, "Payment cannot be completed")
    order.payment_status = PaymentStatus.PAID
    transaction = record(db, order, PaymentTransactionStatus.SUCCESS)
    NotificationService.from_template(db, user.id, "PAYMENT_SUCCESS", "payment_success", "PAYMENT", order.id,
                                      f"payment:{order.id}:success", order_number=order.order_number)
    db.commit()
    return {"status": "PAID", "transaction_id": transaction.transaction_id}


@router.post("/orders/{order_id}/failed")
def payment_failed(order_id: int, request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if settings.rate_limit_enabled: enforce_rate_limit(request, f"payment:order:{user.id}", 20)
    order = db.scalar(select(Order).where(Order.id == order_id, Order.user_id == user.id).with_for_update())
    if not order:
        raise HTTPException(404, "Order not found")
    if order.payment_status == PaymentStatus.FAILED:
        existing = db.scalar(select(PaymentTransaction).where(PaymentTransaction.order_id == order.id, PaymentTransaction.status == PaymentTransactionStatus.FAILED))
        return {"status": "FAILED", "transaction_id": existing.transaction_id if existing else None}
    if order.payment_status == PaymentStatus.PAID:
        raise HTTPException(400, "Paid order cannot be marked failed")
    order.payment_status = PaymentStatus.FAILED
    transaction = record(db, order, PaymentTransactionStatus.FAILED)
    NotificationService.from_template(db, user.id, "PAYMENT_FAILED", "payment_failed", "PAYMENT", order.id,
                                      f"payment:{order.id}:failed", order_number=order.order_number)
    db.commit()
    return {"status": "FAILED", "transaction_id": transaction.transaction_id}


@router.post("/services/{service_type}/{service_id}/success")
def service_payment_success(service_type: str, service_id: int, request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if settings.rate_limit_enabled: enforce_rate_limit(request, f"payment:service:{user.id}", 20)
    try:
        payment_type = PaymentServiceType(service_type.upper())
    except ValueError:
        raise HTTPException(422, "Unsupported payment service") from None
    if payment_type == PaymentServiceType.ORDER:
        raise HTTPException(400, "Use the order payment endpoint")
    if payment_type == PaymentServiceType.PARCEL:
        service = db.scalar(select(Parcel).where(Parcel.id == service_id, Parcel.customer_id == user.id).with_for_update())
        if not service:
            raise HTTPException(404, "Parcel not found")
        if service.payment_status == PaymentStatus.PAID:
            existing = db.scalar(select(PaymentTransaction).where(PaymentTransaction.user_id == user.id, PaymentTransaction.service_type == payment_type, PaymentTransaction.service_id == service_id, PaymentTransaction.status == PaymentTransactionStatus.SUCCESS))
            return {"status": "PAID", "transaction_id": existing.transaction_id if existing else None}
        if service.payment_status != PaymentStatus.PENDING or service.status == ParcelStatus.CANCELLED:
            raise HTTPException(400, "Parcel payment cannot be completed")
        service.payment_status = PaymentStatus.PAID
        amount = service.price
    elif payment_type == PaymentServiceType.RIDE:
        service = db.scalar(select(Ride).where(Ride.id == service_id, Ride.customer_id == user.id).with_for_update())
        if not service:
            raise HTTPException(404, "Ride not found")
        if service.status != RideStatus.RIDE_COMPLETED:
            raise HTTPException(400, "Ride payment is available after completion")
        if service.payment_status == PaymentStatus.PAID:
            existing = db.scalar(select(PaymentTransaction).where(PaymentTransaction.user_id == user.id, PaymentTransaction.service_type == payment_type, PaymentTransaction.service_id == service_id, PaymentTransaction.status == PaymentTransactionStatus.SUCCESS))
            return {"status": "PAID", "transaction_id": existing.transaction_id if existing else None}
        service.payment_status = PaymentStatus.PAID
        amount = service.fare
    else:
        raise HTTPException(400, "Siren payment is not configured")
    existing = db.scalar(select(PaymentTransaction).where(PaymentTransaction.user_id == user.id, PaymentTransaction.service_type == payment_type, PaymentTransaction.service_id == service_id, PaymentTransaction.status == PaymentTransactionStatus.SUCCESS))
    if existing:
        return {"status": "PAID", "transaction_id": existing.transaction_id}
    transaction = record(db, None, PaymentTransactionStatus.SUCCESS, amount=amount, service_type=payment_type, service_id=service_id, user_id=user.id)
    NotificationService.create_notification(db, user.id, "Payment successful", f"Payment successful for your {payment_type.value.lower()}.", "PAYMENT_SUCCESS", payment_type.value, service_id, f"payment:{payment_type.value.lower()}:{service_id}:success")
    db.commit()
    return {"status": "PAID", "transaction_id": transaction.transaction_id}


@router.post("/orders/{order_id}/refund")
def refund(order_id: int, user: User = Depends(require_role(UserRole.ADMIN)), db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    if order.payment_status != PaymentStatus.PAID or order.status not in {OrderStatus.CANCELLED, OrderStatus.DELIVERED}:
        raise HTTPException(400, "Order is not eligible for refund")
    existing = db.scalar(select(PaymentTransaction).where(PaymentTransaction.order_id == order.id, PaymentTransaction.status == PaymentTransactionStatus.REFUNDED))
    if existing:
        return {"status": "REFUNDED", "amount": order.total_amount, "transaction_id": existing.transaction_id}
    order.payment_status = PaymentStatus.REFUNDED
    transaction = record(db, order, PaymentTransactionStatus.REFUNDED)
    NotificationService.create_notification(db, order.user_id, "Refund completed",
                                             f"Your refund of ₹{order.total_amount:.0f} has been completed.",
                                             "REFUND_COMPLETED", "PAYMENT", order.id,
                                             f"refund:{order.id}:completed")
    db.commit()
    return {"status": "REFUNDED", "amount": order.total_amount, "transaction_id": transaction.transaction_id}