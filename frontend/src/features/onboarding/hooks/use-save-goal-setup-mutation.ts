"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { saveGoalSetup } from "@/features/onboarding/api/goals";
import type {
  GoalSetupPayload,
  UserGoalResponse,
} from "@/features/onboarding/types/goals.types";

type Variables = {
  accessToken: string;
  payload: GoalSetupPayload;
};

export function useSaveGoalSetupMutation() {
  const queryClient = useQueryClient();

  return useMutation<UserGoalResponse, Error, Variables>({
    mutationFn: async ({ accessToken, payload }) =>
      saveGoalSetup(accessToken, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["current-goal"] });
      await queryClient.invalidateQueries({ queryKey: ["onboarding-status"] });
    },
  });
}