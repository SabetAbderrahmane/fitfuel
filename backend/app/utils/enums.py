from enum import StrEnum


class GoalType(StrEnum):
    WEIGHT_LOSS = "weight_loss"
    MAINTENANCE = "maintenance"
    MUSCLE_GAIN = "muscle_gain"
    WEIGHT_GAIN = "weight_gain"


class MealType(StrEnum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class PredictionStatus(StrEnum):
    COMPLETED = "completed"
    CONFIRMED = "confirmed"
    CORRECTED = "corrected"


class FeedbackType(StrEnum):
    CONFIRMED = "confirmed"
    CORRECTED = "corrected"