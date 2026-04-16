import { z } from "zod";

const sexOptions = ["male", "female"] as const;

const activityLevelOptions = [
  "sedentary",
  "lightly_active",
  "moderately_active",
  "very_active",
  "extra_active",
] as const;

export const personalDetailsSchema = z.object({
  age: z
    .number()
    .min(15, { message: "Age must be at least 15" })
    .max(120, { message: "Age must be 120 or less" }),

  sex: z.enum(sexOptions, {
    message: "Please select your biological sex.",
  }),

  heightCm: z
    .number()
    .min(50, { message: "Height must be at least 50 cm" })
    .max(200, { message: "Height must be 200 cm or less" }),

  weightKg: z
    .number()
    .min(20, { message: "Weight must be at least 20 kg" })
    .max(500, { message: "Weight must be 500 kg or less" }),

  activityLevel: z.enum(activityLevelOptions, {
    message: "Please select your activity level.",
  }),
});

export type PersonalDetailsFormValues = z.infer<typeof personalDetailsSchema>;