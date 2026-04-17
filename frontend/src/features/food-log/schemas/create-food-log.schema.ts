import { z } from "zod";

const mealTypeOptions = ["breakfast", "lunch", "dinner", "snack"] as const;

export const createFoodLogSchema = z.object({
  loggedForDate: z.string().min(1, { message: "Please choose a date." }),
  mealType: z.enum(mealTypeOptions, {
    message: "Please select a meal type.",
  }),
  notes: z.string().max(2000, { message: "Notes are too long." }).optional(),
  items: z
    .array(
      z.object({
        foodItemId: z.string().min(1),
        quantity: z.number().gt(0).lte(100),
        grams: z.number().gt(0).lte(5000).nullable(),
      })
    )
    .min(1, { message: "Add at least one food item." }),
});

export type CreateFoodLogFormValues = z.infer<typeof createFoodLogSchema>;