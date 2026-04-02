from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session


ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    """
    Small reusable repository base class.
    """

    def __init__(self, db: Session, model: type[ModelT]) -> None:
        self.db = db
        self.model = model

    def get_by_id(self, object_id: str) -> ModelT | None:
        return self.db.get(self.model, object_id)

    def list(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ModelT]:
        statement = (
            select(self.model)
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

    def count(self) -> int:
        total = self.db.scalar(select(func.count()).select_from(self.model))
        return int(total or 0)

    def add(self, instance: ModelT) -> ModelT:
        self.db.add(instance)
        return instance

    def delete(self, instance: ModelT) -> None:
        self.db.delete(instance)

    def flush(self) -> None:
        self.db.flush()

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, instance: ModelT) -> None:
        self.db.refresh(instance)