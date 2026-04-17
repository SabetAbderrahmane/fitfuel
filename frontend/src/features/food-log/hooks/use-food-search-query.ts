"use client";

import { useQuery } from "@tanstack/react-query";

import { searchFoods } from "@/features/food-log/api/food-log";
import type { FoodItemResponse } from "@/features/food-log/types/food-log.types";

export function useFoodSearchQuery(
  accessToken: string | null,
  query: string
) {
  return useQuery<FoodItemResponse[], Error>({
    queryKey: ["food-search", accessToken, query],
    queryFn: async () => searchFoods(accessToken as string, query),
    enabled: Boolean(accessToken),
    retry: 0,
    refetchOnWindowFocus: false,
    staleTime: 10_000,
  });
}