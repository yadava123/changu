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
from app.models import Delivery, DeliveryStatus, Driver, DriverApplication, Order, User, UserRole

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)


def override_get_db():
    with TestingSessionLocal() as db:
        yield db

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def login(email):
    response = client.post("/api/auth/login", json={"email": email, "password": "StrongPassword123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture(autouse=True)
def seed():
    app.dependency_overrides[get_db] = override_get_db
    with TestingSessionLocal() as db:
        db.query(Delivery).delete(); db.query(DriverApplication).delete(); db.query(Driver).delete(); db.query(Order).delete(); db.query(User).delete()
        db.add_all([User(full_name="Customer", email="customer@example.com", phone="9876543210", password_hash=hash_password("StrongPassword123"), role=UserRole.CUSTOMER), User(full_name="Admin", email="admin@example.com", phone="9876543211", password_hash=hash_password("StrongPassword123"), role=UserRole.ADMIN), User(full_name="Driver A", email="drivera@example.com", phone="9876543212", password_hash=hash_password("StrongPassword123"), role=UserRole.CUSTOMER), User(full_name="Driver B", email="driverb@example.com", phone="9876543213", password_hash=hash_password("StrongPassword123"), role=UserRole.CUSTOMER)])
        db.commit()
    yield


def payload(email):
    return {"full_name":"Driver A","phone":"9876543212","email":email,"vehicle_type":"BIKE","vehicle_number":"KA01AB1234","license_number":"LIC12345","address":"1 Main Road","area":"Indiranagar","city":"Bengaluru","state":"Karnataka","pincode":"560038"}


def approve(application_id):
    return client.patch(f"/api/admin/driver-applications/{application_id}", headers=login("admin@example.com"), json={"status":"APPROVED"})


def test_application_approval_and_online_status():
    customer = login("customer@example.com")
    assert client.post("/api/driver/applications", headers=customer, json=payload("customer@example.com")).status_code == 201
    application = client.get("/api/driver/applications/me", headers=customer).json()
    assert client.post("/api/driver/applications", headers=customer, json=payload("customer@example.com")).status_code == 409
    assert approve(application["id"]).status_code == 200
    driver = login("customer@example.com")
    assert client.post("/api/driver/status", headers=driver, json={"is_online":True}).status_code == 200
    assert client.get("/api/driver/status", headers=driver).json()["is_online"] is True


def test_customer_cannot_access_driver_or_admin_driver_api():
    assert client.get("/api/driver/status", headers=login("customer@example.com")).status_code == 403
    assert client.get("/api/admin/drivers", headers=login("customer@example.com")).status_code == 403


def test_admin_can_list_and_deactivate_driver():
    customer = login("customer@example.com")
    client.post("/api/driver/applications", headers=customer, json=payload("customer@example.com"))
    application = client.get("/api/driver/applications/me", headers=customer).json()
    approve(application["id"])
    driver = client.get("/api/admin/drivers", headers=login("admin@example.com"))
    assert driver.status_code == 200
    result = client.patch(f"/api/admin/drivers/{driver.json()[0]['id']}/status", headers=login("admin@example.com"), json={"is_active":False})
    assert result.status_code == 200 and result.json()["is_online"] is False
