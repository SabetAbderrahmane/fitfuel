from dataclasses import dataclass


@dataclass(slots=True)
class MacroTargets:
    calories: int
    protein_g: int
    carbs_g: int
    fat_g: int


def _protein_factor(goal_type: str) -> float:
    normalized_goal = goal_type.strip().lower().replace(" ", "_")

    if normalized_goal == "weight_loss":
        return 2.0
    if normalized_goal == "maintenance":
        return 1.6
    if normalized_goal in {"muscle_gain", "weight_gain"}:
        return 2.2

    raise ValueError(
        "Unsupported goal type. Use one of: weight_loss, maintenance, muscle_gain, weight_gain."
    )


def _fat_factor(goal_type: str) -> float:
    normalized_goal = goal_type.strip().lower().replace(" ", "_")

    if normalized_goal == "weight_loss":
        return 0.8
    if normalized_goal == "maintenance":
        return 0.9
    if normalized_goal in {"muscle_gain", "weight_gain"}:
        return 0.9

    raise ValueError(
        "Unsupported goal type. Use one of: weight_loss, maintenance, muscle_gain, weight_gain."
    )


def calculate_macros(
    target_calories: int,
    weight_kg: float,
    goal_type: str,
) -> MacroTargets:
    """
    Macro allocation strategy:
    - protein based on body weight and goal
    - fat minimum threshold based on body weight
    - carbs receive the remaining calories
    """
    protein_g = round(weight_kg * _protein_factor(goal_type))
    fat_g = round(weight_kg * _fat_factor(goal_type))

    protein_calories = protein_g * 4
    fat_calories = fat_g * 9
    remaining_calories = target_calories - protein_calories - fat_calories

    if remaining_calories < 0:
        raise ValueError(
            "Target calories are too low for the calculated protein/fat minimums."
        )

    carbs_g = round(remaining_calories / 4)

    return MacroTargets(
        calories=target_calories,
        protein_g=int(protein_g),
        carbs_g=int(carbs_g),
        fat_g=int(fat_g),
    )