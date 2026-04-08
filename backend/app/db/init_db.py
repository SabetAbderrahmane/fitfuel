from app.core.database import check_database_connection, create_db_and_tables


def init() -> None:
    if not check_database_connection():
        raise RuntimeError(
            "Database connection failed. Check PostgreSQL, DATABASE_URL, and Docker."
        )

    create_db_and_tables()
    print("Database initialized successfully.")


if __name__ == "__main__":
    init()