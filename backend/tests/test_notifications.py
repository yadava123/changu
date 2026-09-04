import os
os.environ['SECRET_KEY']='test-secret-key'
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Notification, NotificationPreference, User, UserRole
engine=create_engine('sqlite://',connect_args={'check_same_thread':False},poolclass=StaticPool);Session=sessionmaker(bind=engine,autoflush=False,autocommit=False);Base.metadata.create_all(bind=engine)
def override():
    with Session() as db:yield db
app.dependency_overrides[get_db]=override
client=TestClient(app)
def login(email):
    r=client.post('/api/auth/login',json={'email':email,'password':'StrongPassword123'});return {'Authorization':f"Bearer {r.json()['access_token']}"}
def test_notification_lifecycle_and_preferences():
    app.dependency_overrides[get_db]=override
    with Session() as db:
        db.query(Notification).delete();db.query(NotificationPreference).delete();db.query(User).delete();db.add_all([User(full_name='A',email='a@example.com',phone='9876543210',password_hash=hash_password('StrongPassword123'),role=UserRole.CUSTOMER),User(full_name='B',email='b@example.com',phone='9876543211',password_hash=hash_password('StrongPassword123'),role=UserRole.CUSTOMER)]);db.commit()
        a=db.query(User).filter_by(email='a@example.com').first();db.add_all([Notification(user_id=a.id,title='One',message='First',type='ORDER'),Notification(user_id=a.id,title='Two',message='Second',type='SYSTEM')]);db.commit()
    h=login('a@example.com'); assert client.get('/api/notifications?limit=1',headers=h).json()['total']==2;assert client.get('/api/notifications/unread-count',headers=h).json()['count']==2;assert client.patch('/api/notifications/read-all',headers=h).status_code==200;assert client.get('/api/notifications/unread-count',headers=h).json()['count']==0;assert client.patch('/api/notification-preferences',headers=h,json={'order_updates':False}).status_code==200
