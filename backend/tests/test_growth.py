import os
os.environ['SECRET_KEY'] = 'test-secret-key'
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import LoyaltyAccount, LoyaltyTransaction, User, UserRole
from app.services.growth_service import award_order_points

engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
def override_get_db():
    with Session() as db: yield db
app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=engine)
client = TestClient(app)

def token(user): return {'Authorization': f"Bearer {create_access_token(user_id=user.id, email=user.email, role=user.role.value)}"}

def test_loyalty_award_is_idempotent_and_referral_is_single_use():
    with Session() as db:
        db.query(User).delete()
        referrer = User(full_name='Referrer', email='referrer@example.com', phone='9876543210', password_hash=hash_password('StrongPassword123'), role=UserRole.CUSTOMER)
        referred = User(full_name='Referred', email='referred@example.com', phone='9876543211', password_hash=hash_password('StrongPassword123'), role=UserRole.CUSTOMER)
        db.add_all([referrer, referred]); db.commit(); db.refresh(referrer); db.refresh(referred)
        award_order_points(db, referrer.id, 42, Decimal('230')); award_order_points(db, referrer.id, 42, Decimal('230')); db.commit()
        assert db.query(LoyaltyAccount).filter_by(user_id=referrer.id).one().points == 23
        assert db.query(LoyaltyTransaction).filter_by(user_id=referrer.id).count() == 1
        referrer_token, referred_token = token(referrer), token(referred)
    app.dependency_overrides[get_db] = override_get_db
    code = client.get('/api/referrals', headers=referrer_token).json()['code']
    assert client.post('/api/referrals/apply', headers=referred_token, json={'code': code}).status_code == 200
    assert client.post('/api/referrals/apply', headers=referred_token, json={'code': code}).status_code == 409
    assert client.post('/api/referrals/apply', headers=referrer_token, json={'code': code}).status_code == 400
