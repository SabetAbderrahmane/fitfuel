"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { generateMealPlan } from "@/features/meal-plans/api/meal-plans";
import type {
  MealPlanGenerateRequest,
  MealPlanResponse,
} from "@/features/meal-plans/types/meal-plans.types";

type Variables = {
  accessToken: string;
  payload: MealPlanGenerateRequest;
};

export function useGenerateMealPlanMutation() {
  const queryClient = useQueryClient();

  return useMutation<MealPlanResponse, Error, Variables>({
    mutationFn: async ({ accessToken, payload }) =>
      generateMealPlan(accessToken, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["meal-plans-screen"] });
    },
  });
}