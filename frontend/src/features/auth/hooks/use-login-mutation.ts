"use client";

import { useMutation } from "@tanstack/react-query";

import { fetchCurrentUser, loginWithEmail } from "@/features/auth/api/login";
import type {
  AuthenticatedUserResponse,
  LoginRequest,
  TokenResponse,
} from "@/features/auth/types/auth.types";
import { setAuthTokens } from "@/lib/auth/token-storage";

export type LoginMutationVariables = LoginRequest & {
  rememberMe: boolean;
};

export type LoginMutationResult = {
  tokens: TokenResponse;
  user: AuthenticatedUserResponse;
};

export function useLoginMutation() {
  return useMutation<LoginMutationResult, Error, LoginMutationVariables>({
    mutationFn: async ({ rememberMe, ...credentials }) => {
      const tokens = await loginWithEmail(credentials);
      setAuthTokens(tokens, rememberMe);
      const user = await fetchCurrentUser(tokens.access_token);

      return {
        tokens,
        user,
      };
    },
  });
}