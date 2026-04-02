ACTIVITY_MULTIPLIERS: dict[str, float] = {
    "sedentary": 1.2,
    "lightly_active": 1.375,
    "moderately_active": 1.55,
    "very_active": 1.725,
    "extra_active": 1.9,
}


def normalize_activity_level(activity_level: str) -> str:
    normalized = activity_level.strip().lower().replace(" ", "_")
    if normalized not in ACTIVITY_MULTIPLIERS:
        raise ValueError(
            "Unsupported activity level. Use one of: sedentary, lightly_active, "
            "moderately_active, very_active, extra_active."
        )
    return normalized


def calculate_tdee(bmr: float, activity_level: str) -> float:
    normalized_activity = normalize_activity_level(activity_level)
    multiplier = ACTIVITY_MULTIPLIERS[normalized_activity]
    return round(bmr * multiplier, 2)


def calculate_goal_calories(
    tdee: float,
    goal_type: str,
    weekly_target_rate_kg: float | None = None,
) -> int:
    """
    Convert maintenance calories into target calories.

    Approximation:
    1 kg body weight ≈ 7700 kcal
    weekly adjustment ≈ (7700 * weekly_rate_kg) / 7 per day

    For practical thesis implementation we clamp aggressive adjustments
    into a safer daily range.
    """
    normalized_goal = goal_type.strip().lower().replace(" ", "_")

    if normalized_goal == "maintenance":
        return int(round(tdee))

    if weekly_target_rate_kg is None:
        weekly_target_rate_kg = 0.25 if normalized_goal == "weight_loss" else 0.25

    daily_adjustment = abs((7700 * weekly_target_rate_kg) / 7)

    # Keep adjustments within a practical range for a first implementation.
    daily_adjustment = max(250, min(daily_adjustment, 1000))

    if normalized_goal == "weight_loss":
        target = tdee - daily_adjustment
    elif normalized_goal in {"muscle_gain", "weight_gain"}:
        target = tdee + daily_adjustment
    else:
        raise ValueError(
            "Unsupported goal type. Use one of: weight_loss, maintenance, muscle_gain, weight_gain."
        )

    # Simple universal floor/ceiling for MVP stability.
    target = max(1200, min(target, 6000))
    return int(round(target))