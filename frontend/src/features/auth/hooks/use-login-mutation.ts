"use client";

import { useMutation } from "@tanstack/react-query";

import { loginWithEmail } from "@/features/auth/api/login";
import type {
  LoginRequest,
  TokenResponse,
} from "@/features/auth/types/auth.types";
import { setAuthTokens } from "@/lib/auth/token-storage";

export type LoginMutationVariables = LoginRequest & {
  rememberMe: boolean;
};

export function useLoginMutation() {
  return useMutation<TokenResponse, Error, LoginMutationVariables>({
    mutationFn: async ({ rememberMe, ...credentials }) => {
      const tokens = await loginWithEmail(credentials);
      setAuthTokens(tokens, rememberMe);
      return tokens;
    },
  });
}