from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(*, user_id: int, email: str, role: str) -> str:
    if not settings.secret_key:
        raise RuntimeError("SECRET_KEY must be configured before issuing tokens")
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"user_id": user_id, "email": email, "role": role, "exp": expires_at}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    if not settings.secret_key:
        raise JWTError("SECRET_KEY is not configured")
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
