"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { upsertMyProfile } from "@/features/onboarding/api/profile";
import type {
  UserProfileResponse,
  UserProfileUpsertRequest,
} from "@/features/onboarding/types/profile.types";

type Variables = {
  accessToken: string;
  payload: UserProfileUpsertRequest;
};

export function useUpsertProfileMutation() {
  const queryClient = useQueryClient();

  return useMutation<UserProfileResponse, Error, Variables>({
    mutationFn: async ({ accessToken, payload }) =>
      upsertMyProfile(accessToken, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["my-profile"] });
    },
  });
}