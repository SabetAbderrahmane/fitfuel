import type {
  GoalObjectiveUi,
  GoalSetupPayload,
  UserGoalCreateRequest,
  UserGoalResponse,
  UserProfileResponseForGoals,
  UserProfileUpsertRequestForGoals,
} from "@/features/onboarding/types/goals.types";

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

export async function fetchCurrentGoal(
  accessToken: string
): Promise<UserGoalResponse | null> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/goals/current`, {
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
      extractErrorMessage(responseBody) ??
        "Unable to load your current goal."
    );
  }

  return responseBody as UserGoalResponse;
}

export async function fetchProfileForGoals(
  accessToken: string
): Promise<UserProfileResponseForGoals | null> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/users/me/profile`, {
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
      extractErrorMessage(responseBody) ??
        "Unable to load your onboarding profile."
    );
  }

  return responseBody as UserProfileResponseForGoals;
}

export async function upsertProfileForGoals(
  accessToken: string,
  payload: UserProfileUpsertRequestForGoals
): Promise<UserProfileResponseForGoals> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/users/me/profile`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    cache: "no-store",
    body: JSON.stringify(payload),
  });

  const responseBody: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(
      extractErrorMessage(responseBody) ??
        "Unable to save your dietary preferences."
    );
  }

  return responseBody as UserProfileResponseForGoals;
}

export async function createGoal(
  accessToken: string,
  payload: UserGoalCreateRequest
): Promise<UserGoalResponse> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/goals`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    cache: "no-store",
    body: JSON.stringify(payload),
  });

  const responseBody: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(
      extractErrorMessage(responseBody) ??
        "Unable to save your goal."
    );
  }

  return responseBody as UserGoalResponse;
}

export function mapObjectiveToGoalType(
  objective: GoalObjectiveUi
): UserGoalCreateRequest["goal_type"] {
  switch (objective) {
    case "lose":
      return "weight_loss";
    case "gain":
      return "muscle_gain";
    case "maintain":
    default:
      return "maintenance";
  }
}

export async function saveGoalSetup(
  accessToken: string,
  payload: GoalSetupPayload
): Promise<UserGoalResponse> {
  const currentProfile = await fetchProfileForGoals(accessToken);

  if (!currentProfile) {
    throw new Error(
      "Your profile is incomplete. Please complete personal details first."
    );
  }

  const preservedPreferences = currentProfile.dietary_preferences.filter(
    (item) =>
      item.preference_type !== "diet_type" &&
      item.preference_type !== "restriction"
  );

  const nextDietPreferences = payload.dietaryFocus.map((value) => ({
    preference_type: "diet_type" as const,
    value,
    is_active: true,
  }));

  const nextRestrictions = payload.exclusions.map((value) => ({
    preference_type: "restriction" as const,
    value,
    is_active: true,
  }));

  await upsertProfileForGoals(accessToken, {
    first_name: currentProfile.first_name,
    last_name: currentProfile.last_name,
    age: currentProfile.age,
    sex: currentProfile.sex,
    height_cm: currentProfile.height_cm,
    start_weight_kg: currentProfile.start_weight_kg,
    current_weight_kg: currentProfile.current_weight_kg,
    allergies: currentProfile.allergies.map((item) => ({
      allergen_name: item.allergen_name,
      severity: item.severity,
      notes: item.notes,
      is_active: item.is_active,
    })),
    dietary_preferences: [
      ...preservedPreferences.map((item) => ({
        preference_type: item.preference_type,
        value: item.value,
        notes: item.notes,
        is_active: item.is_active,
      })),
      ...nextDietPreferences,
      ...nextRestrictions,
    ],
  });

  return createGoal(accessToken, payload.goal);
}