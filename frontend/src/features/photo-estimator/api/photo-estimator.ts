import type {
  DetectedAnalysisItem,
  FoodItemResponse,
  FoodLogCreateRequest,
  FoodLogResponse,
  PhotoAnalysisResult,
  PhotoUploadResponse,
  VisionInferenceResponse,
  VisionTopPredictionResponse,
} from "@/features/photo-estimator/types/photo-estimator.types";

const tagPositions = [
  { x: 50, y: 70 },
  { x: 25, y: 25 },
  { x: 65, y: 65 },
] as const;

function getApiBaseUrl(): string {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();

  if (!baseUrl) {
    throw new Error(
      "NEXT_PUBLIC_API_BASE_URL is missing. Add it to frontend/.env.local."
    );
  }

  return baseUrl.replace(/\/$/, "");
}

function extractErrorMessage(payload: unknown): string | null {
  if (!payload || typeof payload !== "object" || !("detail" in payload)) {
    return null;
  }

  const detail = (payload as { detail?: unknown }).detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }

        if (
          item &&
          typeof item === "object" &&
          "msg" in item &&
          typeof (item as { msg?: unknown }).msg === "string"
        ) {
          return (item as { msg: string }).msg;
        }

        return null;
      })
      .filter((message): message is string => Boolean(message));

    return messages.length > 0 ? messages.join(", ") : null;
  }

  return null;
}

async function fetchJson<T>(
  path: string,
  accessToken: string,
  init?: RequestInit
): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${accessToken}`,
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  const responseBody: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(
      extractErrorMessage(responseBody) ?? `Request failed for ${path}.`
    );
  }

  return responseBody as T;
}

function prettifyLabel(label: string): string {
  return label
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function buildDetectedItem(
  prediction: VisionTopPredictionResponse,
  foodMatch: FoodItemResponse | null,
  index: number
): DetectedAnalysisItem {
  const servingGrams = Math.round(foodMatch?.default_serving_size_g ?? 100);
  const nutrition = foodMatch?.nutrition_fact;
  const factor = servingGrams / 100;

  const calories = Math.round((nutrition?.calories_per_100g ?? 0) * factor);
  const protein =
    Math.round((nutrition?.protein_g_per_100g ?? 0) * factor * 10) / 10;
  const carbs =
    Math.round((nutrition?.carbs_g_per_100g ?? 0) * factor * 10) / 10;
  const fat = Math.round((nutrition?.fat_g_per_100g ?? 0) * factor * 10) / 10;

  return {
    id: `${prediction.class_index}-${index}-${prediction.label}`,
    name: foodMatch?.name ?? prettifyLabel(prediction.label),
    confidence: Math.round(prediction.confidence_score * 100),
    amount: foodMatch?.default_serving_label ?? `${servingGrams}g serving`,
    calories,
    protein,
    carbs,
    fat,
    weight: servingGrams,
    unit: "g",
    position: tagPositions[index % tagPositions.length],
    foodItemId: foodMatch?.id ?? null,
    per100Calories: nutrition?.calories_per_100g ?? 0,
    per100Protein: nutrition?.protein_g_per_100g ?? 0,
    per100Carbs: nutrition?.carbs_g_per_100g ?? 0,
    per100Fat: nutrition?.fat_g_per_100g ?? 0,
  };
}

export async function uploadPhoto(
  accessToken: string,
  file: File,
  notes?: string | null
): Promise<PhotoUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  if (notes?.trim()) {
    formData.append("notes", notes.trim());
  }

  const response = await fetch(`${getApiBaseUrl()}/api/v1/photos/upload`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    body: formData,
  });

  const responseBody: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(
      extractErrorMessage(responseBody) ?? "Unable to upload photo."
    );
  }

  return responseBody as PhotoUploadResponse;
}

export async function runInference(
  accessToken: string,
  photoUploadId: string
): Promise<VisionInferenceResponse> {
  return fetchJson<VisionInferenceResponse>(
    `/api/v1/photos/${photoUploadId}/run-inference?top_k=3&save_prediction=true`,
    accessToken,
    { method: "POST" }
  );
}

export async function searchFoodMatch(
  accessToken: string,
  label: string
): Promise<FoodItemResponse | null> {
  const params = new URLSearchParams({
    q: label,
    limit: "1",
    offset: "0",
  });

  const result = await fetchJson<FoodItemResponse[]>(
    `/api/v1/meals/foods?${params.toString()}`,
    accessToken
  );

  return result[0] ?? null;
}

export async function analyzePhotoFile(
  accessToken: string,
  file: File
): Promise<PhotoAnalysisResult> {
  const upload = await uploadPhoto(accessToken, file);
  const inference = await runInference(accessToken, upload.id);

  const predictions =
    inference.top_predictions.length > 0
      ? inference.top_predictions.slice(0, 3)
      : [
          {
            class_index: 0,
            label: inference.predicted_label,
            confidence_score: inference.confidence_score,
          },
        ];

  const foodMatches = await Promise.all(
    predictions.map((prediction) => searchFoodMatch(accessToken, prediction.label))
  );

  const items = predictions.map((prediction, index) =>
    buildDetectedItem(prediction, foodMatches[index], index)
  );

  return {
    upload,
    inference,
    items,
  };
}

export async function createPhotoAnalyzedFoodLog(
  accessToken: string,
  payload: FoodLogCreateRequest
): Promise<FoodLogResponse> {
  return fetchJson<FoodLogResponse>("/api/v1/food-logs", accessToken, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}