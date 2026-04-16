export type GoalType =
  | "weight_loss"
  | "maintenance"
  | "muscle_gain"
  | "weight_gain";

export type GoalObjectiveUi = "lose" | "maintain" | "gain";

export type CalculationMode = "calculated" | "manual";

export type BmrFormula = "mifflin_st_jeor" | "harris_benedict";

export type DietaryPreferenceType =
  | "diet_type"
  | "disliked_food"
  | "preferred_food"
  | "restriction";

export type DietaryPreferenceUpsertRequest = {
  preference_type: DietaryPreferenceType;
  value: string;
  notes?: string | null;
  is_active?: boolean;
};

export type UserProfileResponseForGoals = {
  id: string;
  user_id: string;
  first_name: string | null;
  last_name: string | null;
  age: number | null;
  sex: string | null;
  height_cm: number | null;
  start_weight_kg: number | null;
  current_weight_kg: number | null;
  allergies: Array<{
    allergen_name: string;
    severity: string | null;
    notes: string | null;
    is_active: boolean;
  }>;
  dietary_preferences: Array<{
    preference_type: DietaryPreferenceType;
    value: string;
    notes: string | null;
    is_active: boolean;
  }>;
};

export type UserProfileUpsertRequestForGoals = {
  first_name?: string | null;
  last_name?: string | null;
  age?: number | null;
  sex?: string | null;
  height_cm?: number | null;
  start_weight_kg?: number | null;
  current_weight_kg?: number | null;
  activity_profile?: {
    activity_level?: string | null;
    workout_days_per_week?: number | null;
    preferred_workout_style?: string | null;
    daily_step_goal?: number | null;
    notes?: string | null;
  } | null;
  allergies: Array<{
    allergen_name: string;
    severity?: string | null;
    notes?: string | null;
    is_active?: boolean;
  }>;
  dietary_preferences: DietaryPreferenceUpsertRequest[];
};

export type UserGoalCreateRequest = {
  goal_type: GoalType;
  notes?: string | null;
  calculation_mode?: CalculationMode;
  bmr_formula?: BmrFormula;
  target_weight_kg?: number | null;
  weekly_target_rate_kg?: number | null;
  target_calories?: number | null;
  target_protein_g?: number | null;
  target_carbs_g?: number | null;
  target_fat_g?: number | null;
};

export type UserGoalResponse = {
  id: string;
  user_id: string;
  goal_type: GoalType;
  notes: string | null;
  calculation_mode: CalculationMode;
  bmr_formula: BmrFormula | null;
  estimated_bmr: number | null;
  estimated_tdee: number | null;
  target_weight_kg: number | null;
  weekly_target_rate_kg: number | null;
  target_calories: number;
  target_protein_g: number;
  target_carbs_g: number;
  target_fat_g: number;
  is_active: boolean;
  started_at: string;
  ended_at: string | null;
  created_at: string;
  updated_at: string;
};

export type GoalSetupPayload = {
  goal: UserGoalCreateRequest;
  dietaryFocus: string[];
  exclusions: string[];
};