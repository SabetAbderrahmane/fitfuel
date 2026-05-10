from __future__ import annotations

from collections.abc import Generator

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.routes.photos import router as photos_router
from app.db.session import get_db


def test_photo_analyze_requires_auth(db_session: Session) -> None:
    app = FastAPI()
    app.include_router(photos_router, prefix="/api/v1/photos")

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/photos/analyze",
            files={"file": ("test.jpg", b"not-a-real-image", "image/jpeg")},
        )

    app.dependency_overrides.clear()
    assert response.status_code in {401, 403}
