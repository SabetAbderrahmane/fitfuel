from app.core.database import check_database_connection, create_db_and_tables


def init() -> None:
    """
    Initialize the local database schema for early development.

    This is useful before your first Alembic migration exists.
    After migrations are set up, prefer Alembic upgrade commands
    for schema evolution.
    """
    if not check_database_connection():
        raise RuntimeError(
            "Database connection failed. Check PostgreSQL, DATABASE_URL, and Docker."
        )

    create_db_and_tables()
    print("Database initialized successfully.")


if __name__ == "__main__":
    init()