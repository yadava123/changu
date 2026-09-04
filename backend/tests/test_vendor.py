import os

os.environ["SECRET_KEY"] = "test-secret-key"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import User, UserRole, Vendor, Product

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)


def override_get_db():
    with TestingSessionLocal() as db:
        yield db


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def login(email, password="StrongPassword123"):
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture(autouse=True)
def seed():
    app.dependency_overrides[get_db] = override_get_db
    with TestingSessionLocal() as db:
        db.query(Product).delete()
        db.query(Vendor).delete()
        db.query(User).delete()
        db.add_all([
            User(full_name="Customer", email="customer@example.com", phone="9876543210", password_hash=hash_password("StrongPassword123"), role=UserRole.CUSTOMER),
            User(full_name="Admin", email="admin@example.com", phone="9876543211", password_hash=hash_password("StrongPassword123"), role=UserRole.ADMIN),
            User(full_name="Vendor A", email="a@example.com", phone="9876543212", password_hash=hash_password("StrongPassword123"), role=UserRole.VENDOR),
            User(full_name="Vendor B", email="b@example.com", phone="9876543213", password_hash=hash_password("StrongPassword123"), role=UserRole.VENDOR),
        ])
        db.flush()
        db.add_all([
            Vendor(user_id=3, business_name="Store A", business_type="GROCERY", description="A", phone="9876543212", email="a@example.com", address="A", area="A", city="Bengaluru", state="Karnataka", pincode="560001"),
            Vendor(user_id=4, business_name="Store B", business_type="GROCERY", description="B", phone="9876543213", email="b@example.com", address="B", area="B", city="Bengaluru", state="Karnataka", pincode="560002"),
        ])
        db.commit()
    yield


def application_payload():
    return {"business_name":"Riya's Kitchen","business_type":"HOME_CHEF","description":"Fresh meals","phone":"9876543210","email":"customer@example.com","address":"1 Main Road","area":"Indiranagar","city":"Bengaluru","state":"Karnataka","pincode":"560038"}


def test_application_and_duplicate():
    headers = login("customer@example.com")
    assert client.post("/api/vendor/applications", headers=headers, json=application_payload()).status_code == 201
    duplicate = client.post("/api/vendor/applications", headers=headers, json=application_payload())
    assert duplicate.status_code == 409
    assert client.get("/api/vendor/applications/me", headers=headers).json()["status"] == "PENDING"


def test_admin_approval_changes_role_and_creates_vendor():
    customer = login("customer@example.com")
    client.post("/api/vendor/applications", headers=customer, json=application_payload())
    admin = login("admin@example.com")
    applications = client.get("/api/admin/vendor-applications", headers=admin)
    assert applications.status_code == 200
    decision = client.patch(f"/api/admin/vendor-applications/{applications.json()[0]['id']}", headers=admin, json={"status":"APPROVED"})
    assert decision.status_code == 200
    with TestingSessionLocal() as db:
        user = db.get(User, 1)
        assert user.role == UserRole.VENDOR
        assert db.query(Vendor).filter(Vendor.user_id == 1).first() is not None


def test_customer_and_vendor_cannot_approve():
    customer = login("customer@example.com")
    client.post("/api/vendor/applications", headers=customer, json=application_payload())
    application_id = client.get("/api/vendor/applications/me", headers=customer).json()["id"]
    assert client.patch(f"/api/admin/vendor-applications/{application_id}", headers=customer, json={"status":"APPROVED"}).status_code == 403
    assert client.patch(f"/api/admin/vendor-applications/{application_id}", headers=login("a@example.com"), json={"status":"APPROVED"}).status_code == 403


def test_vendor_product_isolation_and_disable():
    a = login("a@example.com")
    b = login("b@example.com")
    created = client.post("/api/vendor/products", headers=a, json={"name":"A Product","description":"A product","price":10,"category":"Grocery","stock_quantity":4,"is_available":True})
    assert created.status_code == 201, created.text
    product_id = created.json()["id"]
    assert len(client.get("/api/vendor/products", headers=a).json()) == 1
    assert client.get(f"/api/vendor/products/{product_id}", headers=b).status_code == 404
    assert client.delete(f"/api/vendor/products/{product_id}", headers=b).status_code == 404
    assert client.delete(f"/api/vendor/products/{product_id}", headers=a).json()["is_available"] is False


def test_vendor_cannot_use_admin_api():
    assert client.get("/api/admin/vendor-applications", headers=login("a@example.com")).status_code == 403
