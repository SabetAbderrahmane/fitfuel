import { z } from "zod";

import type {
  AuthenticatedUserResponse,
  LoginRequest,
  TokenResponse,
} from "@/features/auth/types/auth.types";

const tokenResponseSchema = z.object({
  access_token: z.string().min(1),
  refresh_token: z.string().min(1),
});

const authenticatedUserSchema = z.object({
  id: z.union([z.string(), z.number()]).transform(String),
  email: z.string().email(),
  is_active: z.boolean().optional(),
  is_verified: z.boolean().optional(),
});

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

export async function loginWithEmail(
  payload: LoginRequest
): Promise<TokenResponse> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/auth/login-json`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    cache: "no-store",
    body: JSON.stringify(payload),
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

export async function fetchCurrentUser(
  accessToken: string
): Promise<AuthenticatedUserResponse> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/auth/me`, {
    method: "GET",
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    cache: "no-store",
  });

  const responseBody: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(
      extractErrorMessage(responseBody) ??
        "Unable to fetch the authenticated user."
    );
  }

  return authenticatedUserSchema.parse(responseBody);
}