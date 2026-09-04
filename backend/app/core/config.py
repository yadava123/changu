from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    debug: bool = False
    database_url: str = "sqlite:///./changu.db"
    secret_key: str = ""
    access_token_expire_minutes: int = 60
    delivery_fee: int = 30
    tax_rate: float = 0
    delivery_earning: int = 30
    admin_email: str = ""
    admin_password: str = ""
    vendor_email: str = ""
    vendor_password: str = ""
    ai_provider: str = "rules"
    gemini_api_key: str = ""
    groq_api_key: str = ""
    ai_model: str = "gemini-2.0-flash"
    ai_max_tokens: int = 500
    ai_temperature: float = 0.2
    ai_timeout_seconds: float = 20
    ai_daily_request_limit: int = 30
    rate_limit_enabled: bool = True
    login_rate_limit: int = 10
    register_rate_limit: int = 5
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:5174"]
    db_pool_size: int = 5
    db_max_overflow: int = 5
    db_pool_timeout: int = 30

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


if settings.app_env.lower() == "production":
    if settings.debug:
        raise RuntimeError("DEBUG must be false in production")
    if len(settings.secret_key) < 32 or settings.secret_key.lower().startswith(("replace", "change", "generate")):
        raise RuntimeError("SECRET_KEY must be a generated value of at least 32 characters in production")
    if not settings.database_url.startswith(("postgresql", "postgres")):
        raise RuntimeError("DATABASE_URL must use PostgreSQL in production")
    if not settings.cors_origins or any(origin == "*" for origin in settings.cors_origins):
        raise RuntimeError("CORS_ORIGINS must contain explicit production origins")
