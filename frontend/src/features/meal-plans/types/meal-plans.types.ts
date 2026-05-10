export type MealSlot = "breakfast" | "lunch" | "dinner" | "snack";

export type UserProfileResponse = {
  id: string;
  user_id: string;
  first_name: string | null;
  last_name: string | null;
  age: number | null;
  sex: string | null;
  height_cm: number | null;
  start_weight_kg: number | null;
  current_weight_kg: number | null;
  activity_profile: {
    id: string;
    user_id: string;
    activity_level: string | null;
    workout_days_per_week: number | null;
    preferred_workout_style: string | null;
    daily_step_goal: number | null;
    notes: string | null;
    created_at: string;
    updated_at: string;
  } | null;
  allergies: Array<{
    id: string;
    user_id: string;
    allergen_name: string;
    severity: string | null;
    notes: string | null;
    is_active: boolean;
    created_at: string;
    updated_at: string;
  }>;
  dietary_preferences: Array<{
    id: string;
    user_id: string;
    preference_type: "diet_type" | "disliked_food" | "preferred_food" | "restriction";
    value: string;
    notes: string | null;
    is_active: boolean;
    created_at: string;
    updated_at: string;
  }>;
  created_at: string;
  updated_at: string;
};

export type UserGoalResponse = {
  id: string;
  user_id: string;
  goal_type: "weight_loss" | "maintenance" | "muscle_gain" | "weight_gain";
  notes: string | null;
  calculation_mode: "calculated" | "manual";
  bmr_formula: "mifflin_st_jeor" | "harris_benedict" | null;
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

export type ProgressSnapshotResponse = {
  id: string;
  user_id: string;
  snapshot_date: string;
  current_weight_kg: number | null;
  target_weight_kg: number | null;
  consumed_calories: number;
  consumed_protein_g: number;
  consumed_carbs_g: number;
  consumed_fat_g: number;
  target_calories: number;
  target_protein_g: number;
  target_carbs_g: number;
  target_fat_g: number;
  calorie_adherence_pct: number;
  protein_adherence_pct: number;
  carbs_adherence_pct: number;
  fat_adherence_pct: number;
  overall_adherence_score: number;
  created_at: string;
  updated_at: string;
};

export type MealPlanItemResponse = {
  id: string;
  meal_plan_id: string;
  food_item_id: string;
  meal_slot: MealSlot;
  position: number;
  food_name_snapshot: string;
  brand_snapshot: string | null;
  planned_quantity: number;
  planned_grams: number;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  notes: string | null;
  source_recipe_id?: string | null;
  source_recipe_name?: string | null;
  source_template_id?: string | null;
  source_template_name?: string | null;
  source_generation_type?: string | null;
  created_at: string;
  updated_at: string;
};

export type GroupedMealResponse = {
  meal_slot: MealSlot;
  recipe_name: string | null;
  template_name: string | null;
  source_generation_type: string | null;
  items: MealPlanItemResponse[];
};

export type MealPlanResponse = {
  id: string;
  user_id: string;
  goal_id: string | null;
  plan_date: string;
  generation_mode: "manual" | "rule_based";
  notes: string | null;
  total_calories: number;
  total_protein_g: number;
  total_carbs_g: number;
  total_fat_g: number;
  item_count: number;
  items: MealPlanItemResponse[];
  grouped_meals?: GroupedMealResponse[];
  created_at: string;
  updated_at: string;
};

export type MealPlanGenerateRequest = {
  plan_date: string;
  notes?: string | null;
  meal_slots: MealSlot[];
  preferred_food_item_ids: string[];
  max_items_per_slot: number;
};

export type MealPlansScreenData = {
  profile: UserProfileResponse | null;
  currentGoal: UserGoalResponse | null;
  mealPlans: MealPlanResponse[];
  snapshots: ProgressSnapshotResponse[];
};
