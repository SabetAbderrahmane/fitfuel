"use client";

import { motion } from "framer-motion";

import type {
  DashboardMealSlot,
  MealPlanItemResponse,
  MealPlanResponse,
} from "@/features/dashboard/types/dashboard.types";

const mealSlotOrder: DashboardMealSlot[] = [
  "breakfast",
  "lunch",
  "dinner",
  "snack",
];

const mealSlotImageMap: Record<DashboardMealSlot, string> = {
  breakfast:
    "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&q=80&w=800",
  lunch:
    "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&q=80&w=800",
  dinner:
    "https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&q=80&w=800",
  snack:
    "https://images.unsplash.com/photo-1593095199912-ca4aca6d7903?auto=format&fit=crop&q=80&w=800",
};

function formatSlotLabel(slot: DashboardMealSlot): string {
  switch (slot) {
    case "breakfast":
      return "Breakfast";
    case "lunch":
      return "Lunch";
    case "dinner":
      return "Dinner";
    case "snack":
    default:
      return "Snack";
  }
}

function MealCard({
  item,
  index,
}: Readonly<{
  item: MealPlanItemResponse;
  index: number;
}>) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{
        delay: 0.4 + index * 0.1,
        type: "spring",
        stiffness: 100,
        damping: 20,
      }}
      whileHover={{ y: -8, scale: 1.02, rotateY: index % 2 === 0 ? 2 : -2 }}
      className="dashboard-kinetic-card group cursor-default rounded-2xl"
    >
      <div className="relative h-40 overflow-hidden">
        <img
          src={mealSlotImageMap[item.meal_slot]}
          alt={item.food_name_snapshot}
          className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
          referrerPolicy="no-referrer"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-surface-lowest/80 via-surface-lowest/20 to-transparent" />
      </div>

      <div className="relative space-y-1 p-5">
        <span className="dashboard-glow-green text-[10px] font-black uppercase tracking-[0.2em] text-primary">
          {formatSlotLabel(item.meal_slot)}
        </span>
        <h4 className="text-lg font-bold tracking-tight text-heading">
          {item.food_name_snapshot}
        </h4>
        <p className="text-xs font-semibold text-muted-foreground">
          {Math.round(item.calories)} kcal
        </p>
      </div>

      <motion.div
        className="dashboard-glow-green absolute bottom-0 left-0 h-1 bg-primary"
        initial={{ width: 0 }}
        whileHover={{ width: "100%" }}
        transition={{ duration: 0.3 }}
      />
    </motion.div>
  );
}

type DashboardMealPlanProps = {
  mealPlan: MealPlanResponse | null;
};

export function DashboardMealPlan({
  mealPlan,
}: Readonly<DashboardMealPlanProps>) {
  if (!mealPlan || mealPlan.items.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="font-display text-2xl font-black tracking-tight text-heading">
            Today&apos;s Meal Plan
          </h2>
          <span className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground">
            No Plan Yet
          </span>
        </div>

        <div className="dashboard-kinetic-card rounded-2xl p-8">
          <p className="text-sm font-medium text-muted-foreground">
            No meal plan has been generated yet. Generate one from the meal planning
            flow to see today&apos;s meals here.
          </p>
        </div>
      </div>
    );
  }

  const plannedCards = mealSlotOrder
    .map((slot) => mealPlan.items.find((item) => item.meal_slot === slot))
    .filter((item): item is MealPlanItemResponse => Boolean(item));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="font-display text-2xl font-black tracking-tight text-heading">
          Today&apos;s Meal Plan
        </h2>
        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-primary">
          {mealPlan.plan_date}
        </span>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        {plannedCards.map((meal, index) => (
          <MealCard key={meal.id} item={meal} index={index} />
        ))}
      </div>
    </div>
  );
}