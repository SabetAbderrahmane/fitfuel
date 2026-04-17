"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createPhotoAnalyzedFoodLog } from "@/features/photo-estimator/api/photo-estimator";
import type {
  FoodLogCreateRequest,
  FoodLogResponse,
} from "@/features/photo-estimator/types/photo-estimator.types";

type Variables = {
  accessToken: string;
  payload: FoodLogCreateRequest;
};

export function useCreatePhotoFoodLogMutation() {
  const queryClient = useQueryClient();

  return useMutation<FoodLogResponse, Error, Variables>({
    mutationFn: async ({ accessToken, payload }) =>
      createPhotoAnalyzedFoodLog(accessToken, payload),
    onSuccess: async (_data, variables) => {
      await queryClient.invalidateQueries({
        queryKey: ["dashboard-data", variables.accessToken],
      });
      await queryClient.invalidateQueries({
        queryKey: ["food-log-page", variables.accessToken],
      });
    },
  });
}