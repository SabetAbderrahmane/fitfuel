export type ChatMessageCreateRequest = {
  content: string;
};

export type ChatSessionCreateRequest = {
  title: string | null;
};

export type ChatMessageResponse = {
  id: string;
  chat_session_id: string;
  role: string;
  content: string;
  detected_intent: string | null;
  metadata_json: string | null;
  created_at: string;
  updated_at: string;
};

export type ChatSessionSummaryResponse = {
  id: string;
  user_id: string;
  title: string;
  status: string;
  summary: string | null;
  created_at: string;
  updated_at: string;
};

export type ChatSessionDetailResponse = {
  id: string;
  user_id: string;
  title: string;
  status: string;
  summary: string | null;
  messages: ChatMessageResponse[];
  created_at: string;
  updated_at: string;
};

export type ChatTurnResponse = {
  session_id: string;
  user_message: ChatMessageResponse;
  assistant_message: ChatMessageResponse;
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

export type AssistantPageData = {
  latestSessionSummary: ChatSessionSummaryResponse | null;
  latestSessionDetail: ChatSessionDetailResponse | null;
  currentGoal: UserGoalResponse | null;
  latestSnapshot: ProgressSnapshotResponse | null;
};

export type SendAssistantMessageResult = {
  sessionId: string;
  turn: ChatTurnResponse;
};