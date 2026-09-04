import os
os.environ["SECRET_KEY"]="test-secret-key"
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import EmergencyProvider, EmergencyRequest, ProviderApplication, User, UserRole
engine=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool); Session=sessionmaker(bind=engine,autoflush=False,autocommit=False); Base.metadata.create_all(bind=engine)
def override():
    with Session() as db: yield db
app.dependency_overrides[get_db]=override
client=TestClient(app)
def login(email):
    r=client.post('/api/auth/login',json={'email':email,'password':'StrongPassword123'}); return {'Authorization':f"Bearer {r.json()['access_token']}"}
@pytest.fixture(autouse=True)
def seed():
    app.dependency_overrides[get_db]=override
    with Session() as db:
        db.query(EmergencyRequest).delete();db.query(EmergencyProvider).delete();db.query(ProviderApplication).delete();db.query(User).delete()
        db.add_all([User(full_name='Customer',email='customer@example.com',phone='9876543210',password_hash=hash_password('StrongPassword123'),role=UserRole.CUSTOMER),User(full_name='Admin',email='admin@example.com',phone='9876543211',password_hash=hash_password('StrongPassword123'),role=UserRole.ADMIN),User(full_name='Mechanic',email='mechanic@example.com',phone='9876543212',password_hash=hash_password('StrongPassword123'),role=UserRole.CUSTOMER)])
        db.commit()
    yield

def application(): return {'provider_type':'MECHANIC','business_name':'Demo Auto Care','contact_name':'Mechanic','phone':'9876543212','email':'mechanic@example.com','address':'1 Road','area':'Indiranagar','city':'Bengaluru','state':'Karnataka','pincode':'560038'}
def approve(app_id): return client.patch(f'/api/admin/provider-applications/{app_id}',headers=login('admin@example.com'),json={'status':'APPROVED'})
def test_application_approval_and_status():
    provider=login('mechanic@example.com'); r=client.post('/api/provider/applications',headers=provider,json=application()); assert r.status_code==201; assert client.post('/api/provider/applications',headers=provider,json=application()).status_code==409; assert approve(r.json()['id']).status_code==200
    provider=login('mechanic@example.com'); assert client.post('/api/provider/status',headers=provider,json={'is_online':True}).status_code==200; assert client.get('/api/provider/status',headers=provider).json()['is_online'] is True

def test_customer_isolation_and_matching():
    customer=login('customer@example.com'); r=client.post('/api/emergency/requests',headers=customer,json={'emergency_type':'VEHICLE_BREAKDOWN','description':'Bike stopped','priority':'HIGH','phone':'9876543210','address':'1 Road','area':'Indiranagar','city':'Bengaluru','state':'Karnataka','pincode':'560038'}); assert r.status_code==201; rid=r.json()['id']; assert client.get(f'/api/emergency/requests/{rid}',headers=login('mechanic@example.com')).status_code==404
    assert client.post('/api/emergency/requests',headers=customer,json={'emergency_type':'VEHICLE_BREAKDOWN','description':'Another issue','priority':'HIGH','phone':'9876543210','address':'1 Road','area':'Indiranagar','city':'Bengaluru','state':'Karnataka','pincode':'560038'}).status_code==409
    assert client.post('/api/provider/applications',headers=login('mechanic@example.com'),json=application()).status_code==201

def test_provider_lifecycle():
    customer=login('customer@example.com'); r=client.post('/api/emergency/requests',headers=customer,json={'emergency_type':'VEHICLE_BREAKDOWN','description':'Bike stopped','priority':'HIGH','phone':'9876543210','address':'1 Road','area':'Indiranagar','city':'Bengaluru','state':'Karnataka','pincode':'560038'}); rid=r.json()['id']; client.post('/api/provider/applications',headers=login('mechanic@example.com'),json=application()); aid=client.get('/api/provider/applications/me',headers=login('mechanic@example.com')).json()['id']; approve(aid); provider=login('mechanic@example.com'); client.post('/api/provider/status',headers=provider,json={'is_online':True}); assert client.post(f'/api/provider/requests/{rid}/accept',headers=provider).status_code==200; assert client.post(f'/api/provider/requests/{rid}/on-the-way',headers=provider).status_code==200; assert client.post(f'/api/provider/requests/{rid}/arrived',headers=provider).status_code==200; assert client.post(f'/api/provider/requests/{rid}/resolve',headers=provider).status_code==200
