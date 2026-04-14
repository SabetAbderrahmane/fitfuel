import { z } from "zod";

import type {
  LoginRequest,
  TokenResponse,
} from "@/features/auth/types/auth.types";

const tokenResponseSchema = z.object({
  access_token: z.string().min(1),
  refresh_token: z.string().min(1),
});

function getApiBaseUrl() {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();

  if (!baseUrl) {
    return "";
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

export async function loginWithEmail(
  payload: LoginRequest
): Promise<TokenResponse> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/auth/login-json`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    credentials: "include",
    cache: "no-store",
    body: JSON.stringify({
      email: payload.email,
      password: payload.password,
    }),
  });

  const responseBody: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(
      extractErrorMessage(responseBody) ??
        "Unable to sign in. Please check your credentials and try again."
    );
  }

  return tokenResponseSchema.parse(responseBody);
}