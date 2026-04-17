export type MealType = "breakfast" | "lunch" | "dinner" | "snack";

export type NutritionFactResponse = {
  id: string;
  food_item_id: string;
  calories_per_100g: number;
  protein_g_per_100g: number;
  carbs_g_per_100g: number;
  fat_g_per_100g: number;
  fiber_g_per_100g: number | null;
  sugar_g_per_100g: number | null;
  sodium_mg_per_100g: number | null;
  created_at: string;
  updated_at: string;
};

export type FoodItemResponse = {
  id: string;
  name: string;
  slug: string;
  brand: string | null;
  category: string | null;
  description: string | null;
  default_serving_size_g: number | null;
  default_serving_label: string | null;
  source: string;
  is_active: boolean;
  nutrition_fact: NutritionFactResponse | null;
  created_at: string;
  updated_at: string;
};

export type FoodLogItemCreateRequest = {
  food_item_id: string;
  quantity: number;
  grams: number | null;
};

export type FoodLogCreateRequest = {
  logged_for_date: string;
  meal_type: MealType;
  notes: string | null;
  items: FoodLogItemCreateRequest[];
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
  meal_type: MealType;
  notes: string | null;
  total_calories: number;
  total_protein_g: number;
  total_carbs_g: number;
  total_fat_g: number;
  items: FoodLogItemResponse[];
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

export type FoodLogPageData = {
  currentGoal: UserGoalResponse | null;
  latestSnapshot: ProgressSnapshotResponse | null;
  recentLogs: FoodLogResponse[];
};

export type SelectedFoodItem = {
  food: FoodItemResponse;
  quantity: number;
  grams: number | null;
};

export type CreateFoodLogPreview = {
  loggedForDate: string;
  mealType: MealType;
  notes: string | null;
  selectedItems: SelectedFoodItem[];
};