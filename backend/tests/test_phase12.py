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
from app.models import User, UserEvent, UserPreference, UserRole

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)


def override_get_db():
    with Session() as db:
        yield db


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def auth(user):
    return {"Authorization": f"Bearer {create_access_token(user_id=user.id, email=user.email, role=user.role.value)}"}


def test_preference_controls_and_clear_are_user_scoped():
    with Session() as db:
        db.query(UserEvent).delete()
        db.query(UserPreference).delete()
        db.query(User).delete()
        user = User(full_name="Preference User", email="phase12@example.com", phone="9876543210", password_hash=hash_password("StrongPassword123"), role=UserRole.CUSTOMER)
        db.add(user)
        db.commit()
        db.refresh(user)
    headers = auth(user)
    updated = client.patch("/api/preferences", headers=headers, json={"preferred_categories":["South Indian"],"memory_enabled":False,"recommendations_enabled":False})
    assert updated.status_code == 200
    assert updated.json()["memory_enabled"] is False
    assert client.post("/api/events", headers=headers, json={"event_type":"VIEW_FOOD","entity_type":"FOOD","entity_id":1}).json()["status"] == "disabled"
    assert client.get("/api/recommendations/food", headers=headers).json()["items"] == []
    assert client.delete("/api/preferences", headers=headers).status_code == 204
    assert client.get("/api/preferences", headers=headers).json()["memory_enabled"] is True