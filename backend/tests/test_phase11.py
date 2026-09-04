import os

os.environ["SECRET_KEY"] = "test-secret-key"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Notification, NotificationPreference, Order, OrderStatus, Parcel, ParcelStatus, PaymentMethod, PaymentStatus, PaymentTransaction, Ride, RideStatus, User, UserRole
from app.services.notification_service import NotificationService

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)


def override_get_db():
    with Session() as db:
        yield db


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_user(email="phase11@example.com", reset=True):
    app.dependency_overrides[get_db] = override_get_db
    with Session() as db:
        if reset:
            db.query(Notification).delete()
            db.query(NotificationPreference).delete()
            db.query(User).delete()
        user = User(full_name="Phase 11", email=email, phone="9876543210", password_hash=hash_password("StrongPassword123"), role=UserRole.CUSTOMER)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


def auth(user):
    token = create_access_token(user_id=user.id, email=user.email, role=user.role.value)
    return {"Authorization": f"Bearer {token}"}


def test_notification_service_deduplicates_and_honors_preferences():
    user = setup_user()
    with Session() as db:
        first = NotificationService.create_notification(db, user.id, "One", "First", "ORDER_READY", "ORDER", 1, "order:1:ready")
        duplicate = NotificationService.create_notification(db, user.id, "One", "First", "ORDER_READY", "ORDER", 1, "order:1:ready")
        db.commit()
        assert first is not None
        assert duplicate is None
        db.add(NotificationPreference(user_id=user.id, order_updates=False))
        db.commit()
        suppressed = NotificationService.create_notification(db, user.id, "Two", "Second", "ORDER_READY", "ORDER", 2, "order:2:ready")
        db.commit()
        assert suppressed is None


def test_notification_api_is_user_scoped():
    user = setup_user()
    other = setup_user("other-phase11@example.com", reset=False)
    with Session() as db:
        item = Notification(user_id=user.id, title="Private", message="Only mine", type="SYSTEM")
        db.add(item)
        db.commit()
        item_id = item.id
    assert client.get("/api/notifications", headers=auth(other)).json()["total"] == 0
    assert client.patch(f"/api/notifications/{item_id}/read", headers=auth(other)).status_code == 404


def test_websocket_rejects_missing_or_invalid_authentication():
    from starlette.websockets import WebSocketDisconnect
    try:
        with client.websocket_connect("/ws"):
            raise AssertionError("unauthenticated socket was accepted")
    except WebSocketDisconnect as error:
        assert error.code == 1008
    try:
        with client.websocket_connect("/ws?token=invalid"):
            raise AssertionError("invalid socket was accepted")
    except WebSocketDisconnect as error:
        assert error.code == 1008


def test_payment_success_creates_scoped_transaction_and_is_idempotent():
    user = setup_user()
    with Session() as db:
        order = Order(order_number="CHG99999", user_id=user.id, status=OrderStatus.PENDING, subtotal=100, delivery_fee=30, tax=0, discount=0, total_amount=130, payment_method=PaymentMethod.UPI_MANUAL, payment_status=PaymentStatus.PENDING, delivery_address="Test address")
        db.add(order)
        db.commit()
        db.refresh(order)
        order_id = order.id
    response = client.post(f"/api/payments/orders/{order_id}/success", headers=auth(user))
    assert response.status_code == 200
    transaction_id = response.json()["transaction_id"]
    assert transaction_id.startswith("CHGPAY-")
    repeat = client.post(f"/api/payments/orders/{order_id}/success", headers=auth(user))
    assert repeat.json()["transaction_id"] == transaction_id
    with Session() as db:
        assert db.query(PaymentTransaction).filter_by(order_id=order_id).count() == 1


def test_payment_failure_callback_is_idempotent():
    user = setup_user("payment-failure-phase13@example.com")
    with Session() as db:
        order = Order(order_number="CHG99998", user_id=user.id, status=OrderStatus.PENDING, subtotal=100, delivery_fee=30, tax=0, discount=0, total_amount=130, payment_method=PaymentMethod.UPI_MANUAL, payment_status=PaymentStatus.PENDING, delivery_address="Test address")
        db.add(order)
        db.commit()
        db.refresh(order)
        order_id = order.id
    first = client.post(f"/api/payments/orders/{order_id}/failed", headers=auth(user))
    repeat = client.post(f"/api/payments/orders/{order_id}/failed", headers=auth(user))
    assert first.status_code == repeat.status_code == 200
    assert first.json()["transaction_id"] == repeat.json()["transaction_id"]


def test_ai_requires_auth_and_uses_owned_conversations():
    user = setup_user("ai-phase11@example.com")
    assert client.post("/api/ai/chat", json={"message": "How does ChanGu work?"}).status_code == 401
    response = client.post("/api/ai/chat", headers=auth(user), json={"message": "How does ChanGu work?"})
    assert response.status_code == 200
    conversation_id = response.json()["conversation_id"]
    other = setup_user("ai-other-phase11@example.com", reset=False)
    assert client.get(f"/api/ai/conversations/{conversation_id}", headers=auth(other)).status_code == 404


def test_ai_health_is_admin_only():
    user = setup_user("ai-health-customer@example.com")
    assert client.get("/api/ai/health", headers=auth(user)).status_code == 403
    with Session() as db:
        admin = User(full_name="AI Admin", email="ai-health-admin@example.com", phone="9876543211", password_hash=hash_password("StrongPassword123"), role=UserRole.ADMIN)
        db.add(admin)
        db.commit()
        db.refresh(admin)
    result = client.get("/api/ai/health", headers=auth(admin))
    assert result.status_code == 200
    assert "configured" in result.json() and "available" in result.json()


def test_ai_status_tools_are_ownership_scoped():
    user = setup_user("ai-status@example.com")
    other = setup_user("ai-status-other@example.com", reset=False)
    with Session() as db:
        parcel = Parcel(customer_id=user.id, pickup_address="Pickup", drop_address="Drop", sender_name="Sender", receiver_name="Receiver", parcel_type="BOX", weight_kg=1, price=60, status=ParcelStatus.IN_TRANSIT)
        ride = Ride(customer_id=user.id, pickup_address="Pickup", destination="Drop", ride_type="STANDARD", fare=80, status=RideStatus.DRIVER_ARRIVING)
        db.add_all([parcel, ride])
        db.commit()
        db.refresh(parcel)
        db.refresh(ride)
        parcel_id, ride_id = parcel.id, ride.id
    parcel_response = client.post("/api/ai/chat", headers=auth(user), json={"message": f"Where is parcel #{parcel_id}?"})
    assert parcel_response.status_code == 200
    assert f"Parcel #{parcel_id}" in parcel_response.json()["message"]
    unauthorized = client.post("/api/ai/chat", headers=auth(other), json={"message": f"Where is ride #{ride_id}?"})
    assert unauthorized.status_code == 200
    assert "couldn't find" in unauthorized.json()["message"]
