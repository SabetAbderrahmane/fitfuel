"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchMealPlansScreenData } from "@/features/meal-plans/api/meal-plans";
import type { MealPlansScreenData } from "@/features/meal-plans/types/meal-plans.types";

export function useMealPlansQuery(accessToken: string | null) {
  return useQuery<MealPlansScreenData, Error>({
    queryKey: ["meal-plans-screen", accessToken],
    queryFn: async () => fetchMealPlansScreenData(accessToken as string),
    enabled: Boolean(accessToken),
    retry: 0,
    refetchOnWindowFocus: false,
  });
}