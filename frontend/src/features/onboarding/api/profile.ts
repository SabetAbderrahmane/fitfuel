import type {
  UserProfileResponse,
  UserProfileUpsertRequest,
} from "@/features/onboarding/types/profile.types";

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

export async function fetchMyProfile(
  accessToken: string
): Promise<UserProfileResponse | null> {
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
        "Unable to load your personal profile."
    );
  }

  return responseBody as UserProfileResponse;
}

export async function upsertMyProfile(
  accessToken: string,
  payload: UserProfileUpsertRequest
): Promise<UserProfileResponse> {
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
        "Unable to save your profile. Please try again."
    );
  }

  return responseBody as UserProfileResponse;
}