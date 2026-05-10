from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import Select, desc, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.food_item import FoodItem
from app.models.food_log import FoodLog
from app.models.food_log_item import FoodLogItem
from app.models.user import User
from app.schemas.food_log import FoodLogCreateRequest, FoodLogDailySummaryResponse


class FoodLogService:
    """
    Handles manual meal logging and nutrient snapshot creation.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def _get_food_item_with_nutrition(self, food_item_id: str) -> FoodItem:
        statement = (
            select(FoodItem)
            .options(selectinload(FoodItem.nutrition_fact))
            .where(
                FoodItem.id == food_item_id,
                FoodItem.is_active.is_(True),
            )
        )
        food_item = self.db.scalar(statement)

        if food_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Food item not found: {food_item_id}",
            )

        if food_item.nutrition_fact is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Food item has no nutrition facts: {food_item.name}",
            )

        return food_item

    @staticmethod
    def _resolve_grams(food_item: FoodItem, grams: float | None, quantity: float) -> float:
        if grams is not None:
            return round(grams, 2)

        if food_item.default_serving_size_g is not None:
            return round(food_item.default_serving_size_g * quantity, 2)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Food item '{food_item.name}' requires grams because it has no "
                "default serving size."
            ),
        )

    @staticmethod
    def _scale_nutrient(per_100g: float, grams: float) -> float:
        return round((grams / 100.0) * per_100g, 2)

    def create_food_log(
        self,
        current_user: User,
        payload: FoodLogCreateRequest,
    ) -> FoodLog:
        food_log = FoodLog(
            user_id=current_user.id,
            logged_for_date=payload.logged_for_date,
            meal_type=payload.meal_type,
            source_type="manual",
            notes=payload.notes.strip() if payload.notes else None,
            total_calories=0,
            total_protein_g=0,
            total_carbs_g=0,
            total_fat_g=0,
        )

        total_calories = 0.0
        total_protein = 0.0
        total_carbs = 0.0
        total_fat = 0.0

        for item_payload in payload.items:
            food_item = self._get_food_item_with_nutrition(item_payload.food_item_id)
            nutrition = food_item.nutrition_fact
            grams = self._resolve_grams(
                food_item=food_item,
                grams=item_payload.grams,
                quantity=item_payload.quantity,
            )

            calories = self._scale_nutrient(nutrition.calories_per_100g, grams)
            protein_g = self._scale_nutrient(nutrition.protein_g_per_100g, grams)
            carbs_g = self._scale_nutrient(nutrition.carbs_g_per_100g, grams)
            fat_g = self._scale_nutrient(nutrition.fat_g_per_100g, grams)

            log_item = FoodLogItem(
                food_item_id=food_item.id,
                photo_prediction_id=None,
                food_name_snapshot=food_item.display_name or food_item.name,
                brand_snapshot=food_item.brand,
                serving_name=food_item.default_serving_label,
                source_snapshot={
                    "source_type": "manual",
                    "food_item_source": food_item.source,
                    "catalog_food_item_id": food_item.id,
                },
                quantity=round(item_payload.quantity, 2),
                grams=grams,
                calories=calories,
                protein_g=protein_g,
                carbs_g=carbs_g,
                fat_g=fat_g,
            )

            food_log.items.append(log_item)
            food_item.usage_count = int(food_item.usage_count or 0) + 1

            total_calories += calories
            total_protein += protein_g
            total_carbs += carbs_g
            total_fat += fat_g

        food_log.total_calories = round(total_calories, 2)
        food_log.total_protein_g = round(total_protein, 2)
        food_log.total_carbs_g = round(total_carbs, 2)
        food_log.total_fat_g = round(total_fat, 2)

        self.db.add(food_log)
        self.db.commit()
        self.db.refresh(food_log)

        return self.get_food_log(current_user=current_user, food_log_id=food_log.id)

    def list_food_logs(
        self,
        current_user: User,
        logged_for_date: date | None = None,
        meal_type: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[FoodLog]:
        statement: Select[tuple[FoodLog]] = (
            select(FoodLog)
            .options(selectinload(FoodLog.items))
            .where(FoodLog.user_id == current_user.id)
            .order_by(desc(FoodLog.logged_for_date), desc(FoodLog.created_at))
            .offset(offset)
            .limit(limit)
        )

        if logged_for_date is not None:
            statement = statement.where(FoodLog.logged_for_date == logged_for_date)

        if meal_type is not None:
            statement = statement.where(FoodLog.meal_type == meal_type)

        return list(self.db.scalars(statement).all())

    def get_daily_summary(
        self,
        current_user: User,
        summary_date: date,
    ) -> FoodLogDailySummaryResponse:
        statement = select(
            func.coalesce(func.sum(FoodLog.total_calories), 0.0),
            func.coalesce(func.sum(FoodLog.total_protein_g), 0.0),
            func.coalesce(func.sum(FoodLog.total_carbs_g), 0.0),
            func.coalesce(func.sum(FoodLog.total_fat_g), 0.0),
            func.count(FoodLog.id),
        ).where(
            FoodLog.user_id == current_user.id,
            FoodLog.logged_for_date == summary_date,
        )
        total_calories, total_protein, total_carbs, total_fat, log_count = self.db.execute(statement).one()
        return FoodLogDailySummaryResponse(
            date=summary_date,
            total_calories=round(float(total_calories or 0), 2),
            total_protein_g=round(float(total_protein or 0), 2),
            total_carbs_g=round(float(total_carbs or 0), 2),
            total_fat_g=round(float(total_fat or 0), 2),
            log_count=int(log_count or 0),
        )

    def get_food_log(
        self,
        current_user: User,
        food_log_id: str,
    ) -> FoodLog:
        statement = (
            select(FoodLog)
            .options(selectinload(FoodLog.items))
            .where(
                FoodLog.id == food_log_id,
                FoodLog.user_id == current_user.id,
            )
        )
        food_log = self.db.scalar(statement)

        if food_log is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food log not found.",
            )

        return food_log
