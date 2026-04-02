from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.models.ai_feedback_history import AIFeedbackHistory
from app.models.photo_prediction import PhotoPrediction
from app.models.photo_upload import PhotoUpload
from app.repositories.base import BaseRepository


class PhotoRepository(BaseRepository[PhotoUpload]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, PhotoUpload)

    def get_upload_for_user(
        self,
        user_id: str,
        photo_upload_id: str,
    ) -> PhotoUpload | None:
        return self.db.scalar(
            select(PhotoUpload)
            .options(selectinload(PhotoUpload.predictions))
            .where(
                PhotoUpload.id == photo_upload_id,
                PhotoUpload.user_id == user_id,
            )
        )

    def list_uploads_for_user(
        self,
        user_id: str,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[PhotoUpload]:
        statement = (
            select(PhotoUpload)
            .options(selectinload(PhotoUpload.predictions))
            .where(PhotoUpload.user_id == user_id)
            .order_by(desc(PhotoUpload.created_at))
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

    def get_prediction_for_user(
        self,
        *,
        user_id: str,
        photo_upload_id: str,
        prediction_id: str,
    ) -> PhotoPrediction | None:
        return self.db.scalar(
            select(PhotoPrediction)
            .join(PhotoUpload, PhotoUpload.id == PhotoPrediction.photo_upload_id)
            .where(
                PhotoUpload.user_id == user_id,
                PhotoUpload.id == photo_upload_id,
                PhotoPrediction.id == prediction_id,
            )
        )

    def list_feedback_for_upload(
        self,
        *,
        user_id: str,
        photo_upload_id: str,
    ) -> list[AIFeedbackHistory]:
        statement = (
            select(AIFeedbackHistory)
            .where(
                AIFeedbackHistory.user_id == user_id,
                AIFeedbackHistory.photo_upload_id == photo_upload_id,
            )
            .order_by(desc(AIFeedbackHistory.created_at))
        )
        return list(self.db.scalars(statement).all())