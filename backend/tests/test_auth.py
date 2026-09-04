import os

os.environ["SECRET_KEY"] = "test-secret-key"

from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_current_user, require_role
from app.core.security import ALGORITHM, create_access_token, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User, UserRole

engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)


def override_get_db():
    with TestingSessionLocal() as db:
        yield db


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_users():
    app.dependency_overrides[get_db] = override_get_db
    with TestingSessionLocal() as db:
        db.query(User).delete()
        db.commit()
    yield


def register_user(email="test@example.com"):
    return client.post(
        "/api/auth/register",
        json={
            "full_name": "Test User",
            "email": email,
            "phone": "9876543210",
            "password": "StrongPassword123",
        },
    )


def test_registration_hashes_password_and_defaults_customer():
    response = register_user()
    assert response.status_code == 201
    assert "password" not in response.json()["user"]
    with TestingSessionLocal() as db:
        user = db.scalar(select(User).where(User.email == "test@example.com"))
        assert user is not None
        assert user.password_hash != "StrongPassword123"
        assert user.role == UserRole.CUSTOMER


def test_duplicate_email_returns_conflict():
    register_user()
    response = register_user()
    assert response.status_code == 409
    assert response.json()["detail"] == "An account with this email already exists."


@pytest.mark.parametrize("payload", [
    {"full_name": "", "email": "bad", "phone": "x", "password": "short"},
    {"full_name": "Test", "email": "bad", "phone": "9876543210", "password": "StrongPassword123"},
])
def test_invalid_registration_is_rejected(payload):
    assert client.post("/api/auth/register", json=payload).status_code == 422


def test_login_me_and_invalid_password():
    register_user()
    response = client.post("/api/auth/login", json={"email": "test@example.com", "password": "StrongPassword123"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert jwt.decode(token, "test-secret-key", algorithms=[ALGORITHM])["role"] == "CUSTOMER"
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 200
    invalid = client.post("/api/auth/login", json={"email": "test@example.com", "password": "wrong"})
    assert invalid.status_code == 401


def test_auth_requires_valid_and_active_user():
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer invalid"}).status_code == 401
    register_user()
    with TestingSessionLocal() as db:
        user = db.scalar(select(User).where(User.email == "test@example.com"))
        db.query(User).filter(User.id == user.id).update({"is_active": False})
        db.commit()
    login = client.post("/api/auth/login", json={"email": "test@example.com", "password": "StrongPassword123"})
    assert login.status_code == 401
    assert login.json()["detail"] == "Account is inactive"


def test_expired_token_and_role_dependency():
    register_user()
    with TestingSessionLocal() as db:
        user = db.query(User).filter(User.email == "test@example.com").first()
        expired = jwt.encode({"user_id": user.id, "email": user.email, "role": "CUSTOMER", "exp": 1}, "test-secret-key", algorithm=ALGORITHM)
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired}"}).status_code == 401
    assert user.role == UserRole.CUSTOMER


def test_role_dependency_denies_customer_for_admin():
    register_user()
    login = client.post("/api/auth/login", json={"email": "test@example.com", "password": "StrongPassword123"})
    token = login.json()["access_token"]
    admin_dependency = require_role(UserRole.ADMIN)
    with pytest.raises(Exception) as error:
        with TestingSessionLocal() as db:
            current_user = db.scalar(select(User).where(User.email == "test@example.com"))
            admin_dependency(current_user)
    assert error.value.status_code == 403
