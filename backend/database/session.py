from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from database.models import Base

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create tables if they do not exist."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for API routes to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
