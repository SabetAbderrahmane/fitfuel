"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchFinalPlanSummary } from "@/features/onboarding/api/final-plan";
import type { FinalGoalSummary } from "@/features/onboarding/types/final-plan.types";

export function useFinalPlanQuery(accessToken: string | null) {
  return useQuery<FinalGoalSummary | null, Error>({
    queryKey: ["final-plan-summary", accessToken],
    queryFn: async () => fetchFinalPlanSummary(accessToken as string),
    enabled: Boolean(accessToken),
    retry: 0,
    refetchOnWindowFocus: false,
  });
}