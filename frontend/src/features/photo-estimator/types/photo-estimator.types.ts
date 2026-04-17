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

export type VisionTopPredictionResponse = {
  class_index: number;
  label: string;
  confidence_score: number;
};

export type VisionInferenceResponse = {
  photo_upload_id: string;
  model_name: string;
  predicted_label: string;
  confidence_score: number;
  matched_food_item_id: string | null;
  matched_food_name: string | null;
  match_score: number | null;
  top_predictions: VisionTopPredictionResponse[];
  saved_prediction_id: string | null;
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

export type DetectedAnalysisItem = {
  id: string;
  name: string;
  confidence: number;
  amount: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  weight: number;
  unit: "g";
  position: {
    x: number;
    y: number;
  };
  foodItemId: string | null;
  per100Calories: number;
  per100Protein: number;
  per100Carbs: number;
  per100Fat: number;
};

export type PhotoAnalysisResult = {
  upload: PhotoUploadResponse;
  inference: VisionInferenceResponse;
  items: DetectedAnalysisItem[];
};