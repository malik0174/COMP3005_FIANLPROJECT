# app/init_db.py

import os
import sys

# Ensure the project root (FINALPROJECT) is on sys.path so we can import `database` and `models`.
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import engine, Base
from app.ddl_extras import create_view_index_trigger


# Import all model modules so SQLAlchemy knows about every mapped class.
from models import (
    member,
    trainer,
    admin_staff,
    room,
    trainer_availability,
    session,
) 


def init_db():
    """Create all tables defined by the ORM models."""
    Base.metadata.create_all(bind=engine)
    create_view_index_trigger()
    print("Database tables + view/index/trigger created (or already existed).")


if __name__ == "__main__":
    init_db()