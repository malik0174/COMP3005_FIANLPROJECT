# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from contextlib import contextmanager


DATABASE_URL = "postgresql+psycopg2://postgres:#KemalSQL1938@localhost:5432/health_club_db"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,  # this line will fix commit errors by keeping objects "alive" after commiting 
)

Base = declarative_base()

# BELOW WILL ALLOWS US TO DO "from database import get_session" from anywhere in the project
@contextmanager
def get_session():
    """
    Provide a transactional scope around a series of operations.
    Usage:
        with get_session() as db:
            db.add(obj)
            ...
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()