import os

os.environ["SECRET_KEY"] = "test-secret-key"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import FoodItem, Product, Restaurant, User, UserRole
from app.core.security import hash_password

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)


def override_get_db():
    with TestingSessionLocal() as db:
        yield db


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def seed_catalog():
    app.dependency_overrides[get_db] = override_get_db
    with TestingSessionLocal() as db:
        db.query(Product).delete()
        db.query(FoodItem).delete()
        db.query(Restaurant).delete()
        db.query(User).delete()
        owner = User(full_name="Seed Owner", email="seed@example.com", phone="9876543210", password_hash=hash_password("StrongPassword123"), role=UserRole.CUSTOMER)
        db.add(owner)
        db.flush()
        restaurant = Restaurant(name="Riya's Kitchen", description="Warm home-style meals", owner_id=owner.id, phone="9876543210", address="Indiranagar, Bengaluru", city="Bengaluru", is_active=True)
        db.add(restaurant)
        db.flush()
        db.add(FoodItem(restaurant_id=restaurant.id, name="Chicken Biryani", description="Fragrant basmati and tender chicken", price=220, category="Indian", is_available=True))
        db.add(Product(name="Organic Eggs", description="Farm fresh eggs", price=120, category="Grocery", seller_id=owner.id, stock_quantity=20, is_available=True))
        db.commit()
    yield


def test_restaurants_and_city_filter():
    assert len(client.get("/api/restaurants").json()) == 1
    assert len(client.get("/api/restaurants?city=Bengaluru").json()) == 1
    assert client.get("/api/restaurants?city=Mumbai").json() == []
    assert client.get("/api/restaurants/1").status_code == 200


def test_food_filters_and_details():
    response = client.get("/api/food?search=biryani")
    assert response.status_code == 200
    assert response.json()[0]["name"] == "Chicken Biryani"
    assert client.get("/api/food?restaurant_id=1").json()[0]["restaurant_id"] == 1
    assert client.get("/api/food/1").status_code == 200


def test_products_filters_and_details():
    assert client.get("/api/products?category=Grocery").json()[0]["name"] == "Organic Eggs"
    assert client.get("/api/products?search=eggs").json()[0]["name"] == "Organic Eggs"
    assert client.get("/api/products/1").status_code == 200


@pytest.mark.parametrize("query, result_key, expected", [
    ("biryani", "food", "Chicken Biryani"),
    ("eggs", "products", "Organic Eggs"),
    ("Riya", "restaurants", "Riya's Kitchen"),
])
def test_search(query, result_key, expected):
    response = client.get("/api/search", params={"q": query})
    assert response.status_code == 200
    assert response.json()[result_key][0]["name"] == expected


def test_search_empty_result():
    response = client.get("/api/search?q=not-found")
    assert response.json() == {"restaurants": [], "food": [], "products": []}
