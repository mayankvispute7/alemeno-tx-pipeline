from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# The Engine is the core interface to the database
engine = create_engine(settings.DATABASE_URL, echo=False)

# The SessionLocal class will act as a factory for new database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all our database models (tables) to inherit from
Base = declarative_base()

def get_db():
    """
    Dependency generator that creates a new database session for each request
    and ensures it is closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()