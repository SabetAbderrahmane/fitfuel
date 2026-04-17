"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchFoodLogPageData } from "@/features/food-log/api/food-log";
import type { FoodLogPageData } from "@/features/food-log/types/food-log.types";

export function useFoodLogPageQuery(accessToken: string | null) {
  return useQuery<FoodLogPageData, Error>({
    queryKey: ["food-log-page", accessToken],
    queryFn: async () => fetchFoodLogPageData(accessToken as string),
    enabled: Boolean(accessToken),
    retry: 0,
    refetchOnWindowFocus: false,
  });
}