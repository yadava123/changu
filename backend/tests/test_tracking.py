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
from app.models import Driver, Parcel, User, UserRole

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)
client = TestClient(app)


def override_get_db():
    with Session() as db:
        yield db


def auth(user):
    return {"Authorization": f"Bearer {create_access_token(user_id=user.id, email=user.email, role=user.role.value)}"}


def test_location_requires_online_driver_and_customer_ownership():
    app.dependency_overrides[get_db] = override_get_db
    with Session() as db:
        customer = User(full_name="Tracking Customer", email="tracking-customer@example.com", phone="9876543210", password_hash=hash_password("StrongPassword123"), role=UserRole.CUSTOMER)
        other = User(full_name="Other Customer", email="tracking-other@example.com", phone="9876543211", password_hash=hash_password("StrongPassword123"), role=UserRole.CUSTOMER)
        driver_user = User(full_name="Tracking Driver", email="tracking-driver@example.com", phone="9876543212", password_hash=hash_password("StrongPassword123"), role=UserRole.DRIVER)
        db.add_all([customer, other, driver_user])
        db.flush()
        driver = Driver(user_id=driver_user.id, full_name=driver_user.full_name, phone=driver_user.phone, email=driver_user.email, vehicle_type="BIKE", vehicle_number="KA01", license_number="LIC", address="A", area="A", city="Bengaluru", state="Karnataka", pincode="560001", is_active=True, is_online=False)
        db.add(driver)
        db.flush()
        parcel = Parcel(customer_id=customer.id, driver_id=driver.id, pickup_address="Pickup", drop_address="Drop", sender_name="Sender", receiver_name="Receiver", parcel_type="BOX", weight_kg=1, price=60)
        db.add(parcel)
        db.commit()
        db.refresh(customer); db.refresh(other); db.refresh(driver_user); db.refresh(driver); db.refresh(parcel)
        driver_id = driver.id
    assert client.post("/api/driver/location", headers=auth(driver_user), json={"latitude": 12.9, "longitude": 77.6}).status_code == 400
    with Session() as db:
        db.get(Driver, driver_id).is_online = True
        db.commit()
    assert client.post("/api/driver/location", headers=auth(driver_user), json={"latitude": 12.9, "longitude": 77.6}).status_code == 200
    own = client.get(f"/api/tracking/parcel/{parcel.id}", headers=auth(customer))
    assert own.status_code == 200
    assert own.json()["location"]["latitude"] == 12.9
    assert client.get(f"/api/tracking/parcel/{parcel.id}", headers=auth(other)).status_code == 404
    app.dependency_overrides.pop(get_db, None)
