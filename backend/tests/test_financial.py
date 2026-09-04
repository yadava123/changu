import os

os.environ["SECRET_KEY"] = "test-secret-key"

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import EarningRecord, User, UserRole, Wallet, WalletTransaction
from app.services.financial_service import settle_earning

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)


def override_get_db():
    with Session() as db:
        yield db


client = TestClient(app)


@pytest.fixture(autouse=True)
def financial_db_override():
    previous = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    yield
    if previous is None:
        app.dependency_overrides.pop(get_db, None)
    else:
        app.dependency_overrides[get_db] = previous


def auth(user):
    return {"Authorization": f"Bearer {create_access_token(user_id=user.id, email=user.email, role=user.role.value)}"}


def test_earning_settlement_is_idempotent_and_credits_wallet_once():
    with Session() as db:
        db.query(WalletTransaction).delete()
        db.query(Wallet).delete()
        db.query(EarningRecord).delete()
        db.query(User).delete()
        user = User(full_name="Driver", email="finance-driver@example.com", phone="9876543210", password_hash=hash_password("StrongPassword123"), role=UserRole.DRIVER)
        db.add(user)
        db.commit()
        db.refresh(user)
        first = settle_earning(db, user, "RIDE", 42, Decimal("140.00"))
        second = settle_earning(db, user, "RIDE", 42, Decimal("140.00"))
        db.commit()
        assert first.id == second.id
        assert db.scalar(select(Wallet).where(Wallet.user_id == user.id)).balance == Decimal("140.00")
        assert db.query(WalletTransaction).count() == 1
        assert db.query(EarningRecord).count() == 1


def test_financial_admin_endpoint_requires_admin_role():
    with Session() as db:
        db.query(User).delete()
        customer = User(full_name="Customer", email="finance-customer@example.com", phone="9876543211", password_hash=hash_password("StrongPassword123"), role=UserRole.CUSTOMER)
        db.add(customer)
        db.commit()
        db.refresh(customer)
    assert client.get("/api/admin/financial-summary", headers=auth(customer)).status_code == 403
