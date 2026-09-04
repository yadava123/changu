from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

database_url = settings.database_url or "sqlite:///./changu.db"
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
pool_options = {} if database_url.startswith("sqlite") else {"pool_size": settings.db_pool_size, "max_overflow": settings.db_max_overflow, "pool_timeout": settings.db_pool_timeout}
engine = create_engine(database_url, connect_args=connect_args, pool_pre_ping=True, **pool_options)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
