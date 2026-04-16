export type PreferenceType =
  | "diet_type"
  | "disliked_food"
  | "preferred_food"
  | "restriction";

export type ActivityLevel =
  | "sedentary"
  | "lightly_active"
  | "moderately_active"
  | "very_active"
  | "extra_active";

export type BiologicalSex = "male" | "female";

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

export type AllergyResponse = {
  id: string;
  user_id: string;
  allergen_name: string;
  severity: string | null;
  notes: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type DietaryPreferenceResponse = {
  id: string;
  user_id: string;
  preference_type: PreferenceType;
  value: string;
  notes: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type UserProfileUpsertRequest = {
  first_name?: string | null;
  last_name?: string | null;
  age: number;
  sex: BiologicalSex;
  height_cm: number;
  start_weight_kg: number;
  current_weight_kg: number;
  activity_profile: {
    activity_level: ActivityLevel;
  };
  allergies?: Array<{
    allergen_name: string;
    severity?: string | null;
    notes?: string | null;
    is_active?: boolean;
  }>;
  dietary_preferences?: Array<{
    preference_type: PreferenceType;
    value: string;
    notes?: string | null;
    is_active?: boolean;
  }>;
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
  allergies: AllergyResponse[];
  dietary_preferences: DietaryPreferenceResponse[];
  created_at: string;
  updated_at: string;
};