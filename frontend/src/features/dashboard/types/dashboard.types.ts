export type DashboardMealSlot = "breakfast" | "lunch" | "dinner" | "snack";

export type UserAccountResponse = {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  is_verified: boolean;
};

export type ActivityProfileResponse = {
  id: string;
  user_id: string;
  activity_level: string | null;
  workout_days_per_week: number | null;
  preferred_workout_style: string | null;
  daily_step_goal: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

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
  activity_profile: ActivityProfileResponse | null;
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

export type WeightLogResponse = {
  id: string;
  user_id: string;
  logged_for_date: string;
  weight_kg: number;
  notes: string | null;
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

export type FoodLogDailySummaryResponse = {
  date: string;
  total_calories: number;
  total_protein_g: number;
  total_carbs_g: number;
  total_fat_g: number;
  log_count: number;
};

export type MealPlanItemResponse = {
  id: string;
  meal_plan_id: string;
  food_item_id: string;
  meal_slot: DashboardMealSlot;
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
  created_at: string;
  updated_at: string;
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
  created_at: string;
  updated_at: string;
};

export type FoodLogItemResponse = {
  id: string;
  food_log_id: string;
  food_item_id: string;
  food_name_snapshot: string;
  brand_snapshot: string | null;
  quantity: number;
  grams: number;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  created_at: string;
  updated_at: string;
};

export type FoodLogResponse = {
  id: string;
  user_id: string;
  logged_for_date: string;
  meal_type: DashboardMealSlot;
  notes: string | null;
  total_calories: number;
  total_protein_g: number;
  total_carbs_g: number;
  total_fat_g: number;
  items: FoodLogItemResponse[];
  created_at: string;
  updated_at: string;
};

export type PhotoPredictionResponse = {
  id: string;
  photo_upload_id: string;
  predicted_food_item_id: string | null;
  model_name: string;
  prediction_status: string;
  predicted_label: string;
  confidence_score: number | null;
  estimated_grams: number | null;
  estimated_calories: number | null;
  estimated_protein_g: number | null;
  estimated_carbs_g: number | null;
  estimated_fat_g: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type PhotoUploadResponse = {
  id: string;
  user_id: string;
  original_filename: string;
  content_type: string;
  file_size_bytes: number;
  storage_provider: string;
  storage_key: string;
  storage_url: string | null;
  local_file_path: string | null;
  upload_status: string;
  notes: string | null;
  predictions: PhotoPredictionResponse[];
  created_at: string;
  updated_at: string;
};

export type DashboardData = {
  account: UserAccountResponse;
  profile: UserProfileResponse | null;
  currentGoal: UserGoalResponse | null;
  latestSnapshot: ProgressSnapshotResponse | null;
  dailyFoodLogSummary: FoodLogDailySummaryResponse;
  latestMealPlan: MealPlanResponse | null;
  weightLogs: WeightLogResponse[];
  foodLogs: FoodLogResponse[];
  photoUploads: PhotoUploadResponse[];
};
