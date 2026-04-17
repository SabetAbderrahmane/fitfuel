"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createFoodLog } from "@/features/food-log/api/food-log";
import type {
  CreateFoodLogPreview,
  FoodLogCreateRequest,
  FoodLogPageData,
  FoodLogResponse,
  SelectedFoodItem,
} from "@/features/food-log/types/food-log.types";

type Variables = {
  accessToken: string;
  payload: FoodLogCreateRequest;
  preview: CreateFoodLogPreview;
};

type MutationContext = {
  previousPageData?: FoodLogPageData;
};

function deriveNutrition(item: SelectedFoodItem) {
  const grams = item.grams ?? item.food.default_serving_size_g ?? 100;
  const factor = grams / 100;
  const nutrition = item.food.nutrition_fact;

  return {
    grams,
    calories: Math.round((nutrition?.calories_per_100g ?? 0) * factor),
    protein: Math.round((nutrition?.protein_g_per_100g ?? 0) * factor * 10) / 10,
    carbs: Math.round((nutrition?.carbs_g_per_100g ?? 0) * factor * 10) / 10,
    fat: Math.round((nutrition?.fat_g_per_100g ?? 0) * factor * 10) / 10,
  };
}

export function useCreateFoodLogMutation() {
  const queryClient = useQueryClient();

  return useMutation<FoodLogResponse, Error, Variables, MutationContext>({
    mutationFn: async ({ accessToken, payload }) =>
      createFoodLog(accessToken, payload),

    onMutate: async ({ accessToken, preview }) => {
      const queryKey = ["food-log-page", accessToken];

      await queryClient.cancelQueries({ queryKey });

      const previousPageData = queryClient.getQueryData<FoodLogPageData>(queryKey);

      const now = new Date().toISOString();

      const optimisticItems = preview.selectedItems.map((item, index) => {
        const nutrition = deriveNutrition(item);

        return {
          id: `temp-item-${index}`,
          food_log_id: "temp-log",
          food_item_id: item.food.id,
          food_name_snapshot: item.food.name,
          brand_snapshot: item.food.brand,
          quantity: item.quantity,
          grams: nutrition.grams,
          calories: nutrition.calories,
          protein_g: nutrition.protein,
          carbs_g: nutrition.carbs,
          fat_g: nutrition.fat,
          created_at: now,
          updated_at: now,
        };
      });

      const optimisticLog: FoodLogResponse = {
        id: "temp-log",
        user_id: "temp-user",
        logged_for_date: preview.loggedForDate,
        meal_type: preview.mealType,
        notes: preview.notes,
        total_calories: optimisticItems.reduce((sum, item) => sum + item.calories, 0),
        total_protein_g: optimisticItems.reduce((sum, item) => sum + item.protein_g, 0),
        total_carbs_g: optimisticItems.reduce((sum, item) => sum + item.carbs_g, 0),
        total_fat_g: optimisticItems.reduce((sum, item) => sum + item.fat_g, 0),
        items: optimisticItems,
        created_at: now,
        updated_at: now,
      };

      if (previousPageData) {
        queryClient.setQueryData<FoodLogPageData>(queryKey, {
          ...previousPageData,
          recentLogs: [optimisticLog, ...previousPageData.recentLogs].slice(0, 5),
        });
      }

      return { previousPageData };
    },

    onError: (_error, variables, context) => {
      if (context?.previousPageData) {
        queryClient.setQueryData(
          ["food-log-page", variables.accessToken],
          context.previousPageData
        );
      }
    },

    onSuccess: async (_data, variables) => {
      await queryClient.invalidateQueries({
        queryKey: ["food-log-page", variables.accessToken],
      });
      await queryClient.invalidateQueries({
        queryKey: ["dashboard-data", variables.accessToken],
      });
    },
  });
}