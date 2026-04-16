import { z } from "zod";

const objectiveOptions = ["lose", "maintain", "gain"] as const;

export const goalsSchema = z.object({
  objective: z.enum(objectiveOptions, {
    message: "Please select your primary objective.",
  }),
  weeklyChange: z
    .number()
    .min(0, { message: "Weekly change cannot be negative." })
    .max(1, { message: "Weekly change cannot be more than 1 kg/week." }),
  dietaryFocus: z.array(z.string()),
  exclusions: z.array(z.string()),
});

export type GoalsFormValues = z.infer<typeof goalsSchema>;