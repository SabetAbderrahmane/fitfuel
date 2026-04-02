from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.base import Base
from app.db.session import engine


def create_db_and_tables() -> None:
    """
    Create all registered tables.

    Use this only for early local development/bootstrap.
    Once Alembic is in place, schema changes should be managed
    through migrations instead of create_all().
    """
    Base.metadata.create_all(bind=engine)


def check_database_connection() -> bool:
    """
    Run a lightweight connectivity check against the configured database.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False