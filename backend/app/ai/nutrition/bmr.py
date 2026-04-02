from dataclasses import dataclass


SUPPORTED_SEX_VALUES = {
    "male": "male",
    "m": "male",
    "man": "male",
    "female": "female",
    "f": "female",
    "woman": "female",
}


@dataclass(slots=True)
class BMRInput:
    age: int
    sex: str
    height_cm: float
    weight_kg: float


def normalize_sex(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in SUPPORTED_SEX_VALUES:
        raise ValueError(
            "Unsupported sex value. Use one of: male, female, m, f."
        )
    return SUPPORTED_SEX_VALUES[normalized]


def calculate_mifflin_st_jeor(data: BMRInput) -> float:
    """
    Mifflin–St Jeor equation.

    Male:
        BMR = 10W + 6.25H - 5A + 5

    Female:
        BMR = 10W + 6.25H - 5A - 161

    W = weight in kg
    H = height in cm
    A = age in years
    """
    sex = normalize_sex(data.sex)

    base_value = (10 * data.weight_kg) + (6.25 * data.height_cm) - (5 * data.age)

    if sex == "male":
        return round(base_value + 5, 2)

    return round(base_value - 161, 2)


def calculate_harris_benedict(data: BMRInput) -> float:
    """
    Original Harris–Benedict equation.

    Male:
        BMR = 66.47 + 13.75W + 5.003H - 6.755A

    Female:
        BMR = 655.1 + 9.563W + 1.850H - 4.676A
    """
    sex = normalize_sex(data.sex)

    if sex == "male":
        value = 66.47 + (13.75 * data.weight_kg) + (5.003 * data.height_cm) - (6.755 * data.age)
    else:
        value = 655.1 + (9.563 * data.weight_kg) + (1.850 * data.height_cm) - (4.676 * data.age)

    return round(value, 2)


def calculate_bmr(data: BMRInput, formula: str = "mifflin_st_jeor") -> float:
    normalized_formula = formula.strip().lower()

    if normalized_formula == "mifflin_st_jeor":
        return calculate_mifflin_st_jeor(data)

    if normalized_formula == "harris_benedict":
        return calculate_harris_benedict(data)

    raise ValueError(
        "Unsupported BMR formula. Use 'mifflin_st_jeor' or 'harris_benedict'."
    )