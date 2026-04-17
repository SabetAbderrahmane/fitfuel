import type {
  MealPlanGenerateRequest,
  MealPlanResponse,
  MealPlansScreenData,
  ProgressSnapshotResponse,
  UserGoalResponse,
  UserProfileResponse,
} from "@/features/meal-plans/types/meal-plans.types";

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

async function fetchMaybe404<T>(
  path: string,
  accessToken: string
): Promise<T | null> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    method: "GET",
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    cache: "no-store",
  });

  if (response.status === 404) {
    return null;
  }

  const responseBody: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(
      extractErrorMessage(responseBody) ?? `Request failed for ${path}.`
    );
  }

  return responseBody as T;
}

export async function fetchMealPlansScreenData(
  accessToken: string
): Promise<MealPlansScreenData> {
  const [profile, currentGoal, mealPlans, snapshots] = await Promise.all([
    fetchMaybe404<UserProfileResponse>("/api/v1/users/me/profile", accessToken),
    fetchMaybe404<UserGoalResponse>("/api/v1/goals/current", accessToken),
    fetchJson<MealPlanResponse[]>(
      "/api/v1/meal-plans?limit=7&offset=0",
      accessToken
    ),
    fetchJson<ProgressSnapshotResponse[]>(
      "/api/v1/progress/snapshots?limit=7&offset=0",
      accessToken
    ),
  ]);

  return {
    profile,
    currentGoal,
    mealPlans,
    snapshots,
  };
}

export async function generateMealPlan(
  accessToken: string,
  payload: MealPlanGenerateRequest
): Promise<MealPlanResponse> {
  return fetchJson<MealPlanResponse>("/api/v1/meal-plans/generate", accessToken, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}