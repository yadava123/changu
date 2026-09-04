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
from app.models import Address, Cart, CartItem, Coupon, FoodItem, Restaurant, User, UserRole

engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)
def override_get_db():
    with Session() as db: yield db
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_coupon_discount_is_calculated_and_usage_recorded():
    with Session() as db:
        db.query(User).delete()
        user = User(full_name='Coupon User', email='coupon@example.com', phone='9876543210', password_hash=hash_password('StrongPassword123'), role=UserRole.CUSTOMER)
        db.add(user); db.flush()
        address = Address(user_id=user.id, full_name='Coupon User', phone='9876543210', address_line='1 Main Road', area='Indiranagar', city='Bengaluru', state='Karnataka', pincode='560038')
        restaurant = Restaurant(name='Coupon Kitchen', description='Test', owner_id=user.id, phone='9876543210', address='Test', city='Bengaluru')
        db.add_all([address, restaurant]); db.flush()
        food = FoodItem(restaurant_id=restaurant.id, name='Meal', description='Test', price=100, category='Indian')
        db.add(food); db.flush()
        cart = Cart(user_id=user.id); db.add(cart); db.flush(); db.add(CartItem(cart_id=cart.id, food_item_id=food.id, quantity=2, unit_price=food.price))
        db.add(Coupon(code='SAVE10', discount_percent=10, minimum_order_amount=100, per_user_limit=1)); db.commit()
        token = create_access_token(user_id=user.id, email=user.email, role=user.role.value)
        address_id = address.id
    app.dependency_overrides[get_db] = override_get_db
    response = client.post('/api/orders', headers={'Authorization': f'Bearer {token}'}, json={'address_id': address_id, 'payment_method': 'CASH_ON_DELIVERY', 'coupon_code': 'save10'})
    assert response.status_code == 201
    data = response.json(); assert data['discount'] == '20.00'; assert data['total_amount'] == '210.00'
    with Session() as db:
        assert db.query(Coupon).filter_by(code='SAVE10').one().id is not None
