import type { OnboardingStatus } from "@/features/onboarding/types/onboarding.types";

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

async function resourceExists(
  path: string,
  accessToken: string
): Promise<boolean> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    method: "GET",
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    cache: "no-store",
  });

  if (response.status === 404) {
    return false;
  }

  if (!response.ok) {
    const responseBody: unknown = await response.json().catch(() => null);

    throw new Error(
      extractErrorMessage(responseBody) ??
        `Unable to check onboarding status for ${path}.`
    );
  }

  return true;
}

export async function fetchOnboardingStatus(
  accessToken: string
): Promise<OnboardingStatus> {
  const [hasProfile, hasGoal] = await Promise.all([
    resourceExists("/api/v1/users/me/profile", accessToken),
    resourceExists("/api/v1/goals/current", accessToken),
  ]);

  const isComplete = hasProfile && hasGoal;

  return {
    hasProfile,
    hasGoal,
    isComplete,
    nextRoute: isComplete ? "/dashboard" : "/welcome",
  };
}

export async function resolvePostLoginRoute(
  accessToken: string
): Promise<"/welcome" | "/dashboard"> {
  const status = await fetchOnboardingStatus(accessToken);
  return status.nextRoute;
}