from __future__ import annotations

from app.data_ingestion.normalization import (
    DEFAULT_SOURCE_DEFINITIONS,
    get_or_create_data_source,
)
from app.db.session import SessionLocal


def main() -> None:
    db = SessionLocal()
    try:
        created_or_updated = 0
        for source_code, payload in DEFAULT_SOURCE_DEFINITIONS.items():
            get_or_create_data_source(
                db,
                source_code=source_code,
                display_name=payload["display_name"],
                source_type=payload["source_type"],
                license_name=payload.get("license_name"),
                homepage_url=payload.get("homepage_url"),
            )
            created_or_updated += 1

        db.commit()
        print(f"Seeded/verified {created_or_updated} data source definitions.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()