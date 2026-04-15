"use client";

import { useMutation } from "@tanstack/react-query";

import { registerUser } from "@/features/auth/api/register";
import type {
  AuthenticatedUserResponse,
  RegisterRequest,
} from "@/features/auth/types/auth.types";

export function useRegisterMutation() {
  return useMutation<AuthenticatedUserResponse, Error, RegisterRequest>({
    mutationFn: registerUser,
  });
}