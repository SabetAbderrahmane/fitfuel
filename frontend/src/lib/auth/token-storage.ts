import type { TokenResponse } from "@/features/auth/types/auth.types";

const ACCESS_TOKEN_KEY = "fitfuel.access_token";
const REFRESH_TOKEN_KEY = "fitfuel.refresh_token";

export function clearAuthTokens() {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_TOKEN_KEY);
  window.sessionStorage.removeItem(ACCESS_TOKEN_KEY);
  window.sessionStorage.removeItem(REFRESH_TOKEN_KEY);
}

export function setAuthTokens(tokens: TokenResponse, rememberMe: boolean) {
  if (typeof window === "undefined") {
    return;
  }

  clearAuthTokens();

  const storage = rememberMe ? window.localStorage : window.sessionStorage;

  storage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
  storage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
}

export function getAccessToken() {
  if (typeof window === "undefined") {
    return null;
  }

  return (
    window.localStorage.getItem(ACCESS_TOKEN_KEY) ??
    window.sessionStorage.getItem(ACCESS_TOKEN_KEY)
  );
}

export function getRefreshToken() {
  if (typeof window === "undefined") {
    return null;
  }

  return (
    window.localStorage.getItem(REFRESH_TOKEN_KEY) ??
    window.sessionStorage.getItem(REFRESH_TOKEN_KEY)
  );
}