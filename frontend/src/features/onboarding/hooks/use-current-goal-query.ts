"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchCurrentGoal } from "@/features/onboarding/api/goals";
import type { UserGoalResponse } from "@/features/onboarding/types/goals.types";

export function useCurrentGoalQuery(accessToken: string) {
  return useQuery<UserGoalResponse | null, Error>({
    queryKey: ["current-goal"],
    queryFn: async () => fetchCurrentGoal(accessToken),
    enabled: Boolean(accessToken),
    retry: 0,
    refetchOnWindowFocus: false,
  });
}