import os
os.environ['SECRET_KEY'] = 'test-secret-key'
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Driver, Parcel, PaymentStatus, Ride, RideStatus, User, UserRole

engine=create_engine('sqlite://',connect_args={'check_same_thread':False},poolclass=StaticPool)
Session=sessionmaker(bind=engine,autoflush=False,autocommit=False)
Base.metadata.create_all(bind=engine)
def override_get_db():
    with Session() as db: yield db
app.dependency_overrides[get_db]=override_get_db
client=TestClient(app)
def auth(user): return {'Authorization':f"Bearer {create_access_token(user_id=user.id,email=user.email,role=user.role.value)}"}

def test_customer_transport_creation_and_ownership():
    with Session() as db:
        db.query(Parcel).delete(); db.query(Ride).delete(); db.query(User).delete()
        user=User(full_name='Transport Customer',email='transport@example.com',phone='9876543210',password_hash=hash_password('StrongPassword123'),role=UserRole.CUSTOMER)
        other=User(full_name='Other Customer',email='other-transport@example.com',phone='9876543211',password_hash=hash_password('StrongPassword123'),role=UserRole.CUSTOMER)
        db.add_all([user,other]);db.commit();db.refresh(user);db.refresh(other)
    app.dependency_overrides[get_db]=override_get_db
    parcel=client.post('/api/parcels',headers=auth(user),json={'pickup_address':'Pickup','drop_address':'Drop','sender_name':'Sender','receiver_name':'Receiver','parcel_type':'BOX','weight_kg':2})
    assert parcel.status_code==201 and parcel.json()['price']=='70.00' and parcel.json()['payment_status']=='PENDING'
    payment=client.post(f"/api/payments/services/PARCEL/{parcel.json()['id']}/success",headers=auth(user))
    assert payment.status_code==200 and payment.json()['status']=='PAID'
    ride=client.post('/api/rides',headers=auth(user),json={'pickup_address':'Pickup','destination':'Drop','ride_type':'PREMIUM'})
    assert ride.status_code==201 and ride.json()['fare']=='140.00'
    duplicate=client.post('/api/rides',headers=auth(user),json={'pickup_address':'Pickup 2','destination':'Drop 2','ride_type':'STANDARD'})
    assert duplicate.status_code==409
    with Session() as db:
        db.get(Ride, ride.json()['id']).status = RideStatus.RIDE_COMPLETED
        db.commit()
    ride_payment=client.post(f"/api/payments/services/RIDE/{ride.json()['id']}/success",headers=auth(user))
    assert ride_payment.status_code==200 and ride_payment.json()['status']=='PAID'
    assert client.get(f"/api/parcels/{parcel.json()['id']}",headers=auth(other)).status_code==404
    assert client.get(f"/api/rides/{ride.json()['id']}",headers=auth(other)).status_code==404

def test_driver_can_claim_transport_request_once():
    with Session() as db:
        db.query(Parcel).delete();db.query(User).delete()
        customer=User(full_name='Customer',email='customer-transport@example.com',phone='9876543210',password_hash=hash_password('StrongPassword123'),role=UserRole.CUSTOMER)
        driver=User(full_name='Driver',email='driver-transport@example.com',phone='9876543211',password_hash=hash_password('StrongPassword123'),role=UserRole.DRIVER)
        db.add_all([customer,driver]);db.flush();db.add(Driver(user_id=driver.id,full_name='Driver',phone='9876543211',email=driver.email,vehicle_type='BIKE',vehicle_number='KA01',license_number='LIC1',address='Address',area='Area',city='Bengaluru',state='Karnataka',pincode='560001',is_active=True,is_online=True));db.add(Parcel(customer_id=customer.id,pickup_address='Pickup',drop_address='Drop',sender_name='Sender',receiver_name='Receiver',parcel_type='BOX',weight_kg=1,price=60,payment_status=PaymentStatus.PAID));db.commit();db.refresh(driver)
    app.dependency_overrides[get_db]=override_get_db
    available=client.get('/api/driver/parcels/available',headers=auth(driver));assert available.status_code==200
    parcel_id=available.json()[0]['id']; assert client.post(f'/api/driver/parcels/{parcel_id}/accept',headers=auth(driver)).status_code==200
    assert client.post(f'/api/driver/parcels/{parcel_id}/accept',headers=auth(driver)).status_code==409
