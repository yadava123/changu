import os

os.environ["SECRET_KEY"] = "test-secret-key"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Address, Cart, FoodItem, Order, OrderStatus, Product, Restaurant, User, UserRole

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)


def override_get_db():
    with TestingSessionLocal() as db:
        yield db


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def auth(email):
    response = client.post("/api/auth/login", json={"email": email, "password": "StrongPassword123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture(autouse=True)
def seed():
    app.dependency_overrides[get_db] = override_get_db
    with TestingSessionLocal() as db:
        db.query(Order).delete()
        db.query(Address).delete()
        db.query(Cart).delete()
        db.query(FoodItem).delete()
        db.query(Restaurant).delete()
        db.query(Product).delete()
        db.query(User).delete()
        owner = User(full_name="Owner", email="owner@example.com", phone="9876543210", password_hash=hash_password("StrongPassword123"), role=UserRole.CUSTOMER)
        other = User(full_name="Other", email="other@example.com", phone="9876543211", password_hash=hash_password("StrongPassword123"), role=UserRole.CUSTOMER)
        db.add_all([owner, other])
        db.flush()
        restaurant = Restaurant(name="Test Kitchen", description="Test", owner_id=owner.id, phone="9876543210", address="Test", city="Bengaluru")
        other_restaurant = Restaurant(name="Other Kitchen", description="Test", owner_id=other.id, phone="9876543211", address="Test", city="Bengaluru")
        db.add_all([restaurant, other_restaurant])
        db.flush()
        db.add_all([FoodItem(restaurant_id=restaurant.id, name="Biryani", description="Test", price=100, category="Indian"), FoodItem(restaurant_id=other_restaurant.id, name="Other Food", description="Test", price=50, category="Indian"), Product(seller_id=owner.id, name="Tea", description="Test", price=20, category="Beverages", stock_quantity=2)])
        db.commit()
    yield


def address(headers):
    return client.post("/api/addresses", headers=headers, json={"full_name": "Owner", "phone": "9876543210", "address_line": "1 Main Road", "area": "Indiranagar", "city": "Bengaluru", "state": "Karnataka", "pincode": "560038", "is_default": True}).json()


def test_cart_merge_and_incompatible_source():
    headers = auth("owner@example.com")
    first = client.post("/api/cart/items", headers=headers, json={"food_item_id": 1, "quantity": 2})
    second = client.post("/api/cart/items", headers=headers, json={"food_item_id": 1, "quantity": 1})
    assert first.status_code == second.status_code == 200
    assert second.json()["items"][0]["quantity"] == 3
    assert client.post("/api/cart/items", headers=headers, json={"food_item_id": 2, "quantity": 1}).status_code == 409
    assert client.delete("/api/cart", headers=headers).status_code == 200
    assert client.get("/api/cart", headers=headers).json()["items"] == []


def test_order_calculates_totals_snapshots_items_and_clears_cart():
    headers = auth("owner@example.com")
    client.post("/api/cart/items", headers=headers, json={"food_item_id": 1, "quantity": 2})
    created = client.post("/api/orders", headers=headers, json={"address_id": address(headers)["id"], "payment_method": "CASH_ON_DELIVERY"})
    assert created.status_code == 201
    data = created.json()
    assert data["subtotal"] == "200.00"
    assert data["delivery_fee"] == "30.00"
    assert data["total_amount"] == "230.00"
    assert data["payment_status"] == "PENDING"
    assert data["items"][0]["item_name"] == "Biryani"
    assert client.get("/api/cart", headers=headers).json()["items"] == []


def test_orders_are_private_and_cancellation_is_restricted():
    owner_headers = auth("owner@example.com")
    other_headers = auth("other@example.com")
    client.post("/api/cart/items", headers=owner_headers, json={"food_item_id": 1, "quantity": 1})
    order = client.post("/api/orders", headers=owner_headers, json={"address_id": address(owner_headers)["id"], "payment_method": "CASH_ON_DELIVERY"}).json()
    assert client.get(f"/api/orders/{order['id']}", headers=other_headers).status_code == 404
    cancelled = client.post(f"/api/orders/{order['id']}/cancel", headers=owner_headers)
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "CANCELLED"
    assert client.post(f"/api/orders/{order['id']}/cancel", headers=owner_headers).status_code == 400


def test_checkout_decrements_product_stock_and_rejects_stale_store():
    headers = auth("owner@example.com")
    client.post("/api/cart/items", headers=headers, json={"product_id": 1, "quantity": 2})
    created = client.post("/api/orders", headers=headers, json={"address_id": address(headers)["id"], "payment_method": "CASH_ON_DELIVERY"})
    assert created.status_code == 201
    with TestingSessionLocal() as db:
        assert db.get(Product, 1).stock_quantity == 0
        db.get(Restaurant, 1).is_active = False
        db.commit()
    assert client.post("/api/cart/items", headers=headers, json={"food_item_id": 1, "quantity": 1}).status_code == 400
