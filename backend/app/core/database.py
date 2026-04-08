from __future__ import annotations

from sqlalchemy import text

from app.db.base import Base
from app.db.session import engine


def check_database_connection() -> bool:
    """
    Verify that SQLAlchemy can open a connection to the configured database.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def create_db_and_tables() -> None:
    """
    Import all model modules, then create tables.
    Importing here avoids circular imports in app.db.base.
    """
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)