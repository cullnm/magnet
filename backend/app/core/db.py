from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create the SQLAlchemy engine
engine = create_engine(settings.DATABASE_URL, future=True, pool_pre_ping=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    FastAPI dependency that yields a DB session
    and makes sure it's closed afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()