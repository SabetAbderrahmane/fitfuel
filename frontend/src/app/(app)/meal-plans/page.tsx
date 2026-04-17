"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  AnimatePresence,
  motion,
  useMotionValue,
  useSpring,
  useTransform,
} from "framer-motion";
import {
  BookOpen,
  Calendar,
  Check,
  CheckCircle2,
  ChevronRight,
  Flame,
  RefreshCw,
  Search,
  ShoppingCart,
  Sparkles,
  Target,
  Zap,
  Activity,
} from "lucide-react";

import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { useGenerateMealPlanMutation } from "@/features/meal-plans/hooks/use-generate-meal-plan-mutation";
import { useMealPlansQuery } from "@/features/meal-plans/hooks/use-meal-plans-query";
import type {
  MealPlanItemResponse,
  MealPlanResponse,
  MealPlansScreenData,
  MealSlot,
} from "@/features/meal-plans/types/meal-plans.types";
import { cn } from "@/lib/utils/cn";
import { getAccessToken } from "@/lib/auth/token-storage";

type MacroInfo = {
  label: string;
  value: string;
  unit: string;
  colorClass: string;
  progress: number;
  icon: React.ReactNode;
};

type InventoryItem = {
  id: string;
  name: string;
  amount: string;
  completed: boolean;
};

const dayNames = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
] as const;

const mealImages: Record<MealSlot, string> = {
  breakfast:
    "https://images.unsplash.com/photo-1525351484163-7529414344d8?q=80&w=800&auto=format&fit=crop",
  lunch:
    "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?q=80&w=800&auto=format&fit=crop",
  dinner:
    "https://images.unsplash.com/photo-1467003909585-2f8a72700288?q=80&w=800&auto=format&fit=crop",
  snack:
    "https://images.unsplash.com/photo-1505252585461-04db1eb84625?q=80&w=800&auto=format&fit=crop",
};

function startOfWeek(date: Date): Date {
  const copy = new Date(date);
  const day = copy.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  copy.setDate(copy.getDate() + diff);
  copy.setHours(0, 0, 0, 0);
  return copy;
}

function addDays(date: Date, amount: number): Date {
  const copy = new Date(date);
  copy.setDate(copy.getDate() + amount);
  return copy;
}

function toIsoDate(date: Date): string {
  return date.toISOString().slice(0, 10);
}

function formatRange(start: string, end: string): string {
  const startDate = new Date(start);
  const endDate = new Date(end);

  const formatter = new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
  });

  return `${formatter.format(startDate)} - ${formatter.format(endDate)}`;
}

function formatMealTime(slot: MealSlot): string {
  switch (slot) {
    case "breakfast":
      return "08:30 AM";
    case "lunch":
      return "01:00 PM";
    case "dinner":
      return "07:30 PM";
    case "snack":
    default:
      return "Post-Workout";
  }
}

function formatMealType(slot: MealSlot): string {
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

function clampPercentage(value: number): number {
  return Math.max(0, Math.min(100, Math.round(value)));
}

function deriveMacroStats(data: MealPlansScreenData): MacroInfo[] {
  const goal = data.currentGoal;
  const snapshots = data.snapshots;

  const avgAdherence =
    snapshots.length > 0
      ? snapshots.reduce((sum, snapshot) => sum + snapshot.overall_adherence_score, 0) /
        snapshots.length
      : 0;

  const avgCalorieAdherence =
    snapshots.length > 0
      ? snapshots.reduce((sum, snapshot) => sum + snapshot.calorie_adherence_pct, 0) /
        snapshots.length
      : 0;

  const avgProteinAdherence =
    snapshots.length > 0
      ? snapshots.reduce((sum, snapshot) => sum + snapshot.protein_adherence_pct, 0) /
        snapshots.length
      : 0;

  const avgCarbAdherence =
    snapshots.length > 0
      ? snapshots.reduce((sum, snapshot) => sum + snapshot.carbs_adherence_pct, 0) /
        snapshots.length
      : 0;

  const avgFatAdherence =
    snapshots.length > 0
      ? snapshots.reduce((sum, snapshot) => sum + snapshot.fat_adherence_pct, 0) /
        snapshots.length
      : 0;

  return [
    {
      label: "Avg Daily Fuel",
      value: goal ? goal.target_calories.toLocaleString() : "—",
      unit: "kcal",
      colorClass: "text-slate-400",
      progress: clampPercentage(avgCalorieAdherence || avgAdherence),
      icon: <Flame className="h-4 w-4" />,
    },
    {
      label: "Protein Core",
      value: goal ? goal.target_protein_g.toLocaleString() : "—",
      unit: "grams",
      colorClass: "text-primary",
      progress: clampPercentage(avgProteinAdherence || avgAdherence),
      icon: <Zap className="h-4 w-4" />,
    },
    {
      label: "Energy Carbs",
      value: goal ? goal.target_carbs_g.toLocaleString() : "—",
      unit: "grams",
      colorClass: "text-secondary",
      progress: clampPercentage(avgCarbAdherence || avgAdherence),
      icon: <Activity className="h-4 w-4" />,
    },
    {
      label: "Healthy Fats",
      value: goal ? goal.target_fat_g.toLocaleString() : "—",
      unit: "grams",
      colorClass: "text-tertiary",
      progress: clampPercentage(avgFatAdherence || avgAdherence),
      icon: <Target className="h-4 w-4" />,
    },
  ];
}

function MacroStatCard({
  stat,
}: Readonly<{
  stat: MacroInfo;
}>) {
  return (
    <motion.div
      whileHover={{ y: -5, scale: 1.01, perspective: 1000 }}
      initial={{ opacity: 0, y: 15 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="relative overflow-hidden rounded-lg border border-[rgba(78,222,163,0.15)] bg-gradient-to-br from-[rgba(46,53,69,0.6)] to-[rgba(20,27,43,0.8)] p-5 transition-all"
    >
      <div className="absolute right-2.5 top-2.5 opacity-5">{stat.icon}</div>

      <span className={cn("mb-1 block text-[9px] font-black uppercase tracking-widest", stat.colorClass)}>
        {stat.label}
      </span>

      <div className="flex items-baseline gap-1">
        <span className="font-headline text-2xl font-black text-on-surface">
          {stat.value}
        </span>
        <span className="text-xs font-bold text-slate-500">{stat.unit}</span>
      </div>

      <div className="mt-3 flex items-center gap-2">
        <div className="h-1 w-full overflow-hidden rounded-full bg-surface-container-highest/30">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${stat.progress}%` }}
            transition={{ duration: 1.2, ease: "circOut" }}
            className={cn(
              "h-full",
              stat.colorClass === "text-primary"
                ? "bg-primary"
                : stat.colorClass === "text-secondary"
                ? "bg-secondary"
                : stat.colorClass === "text-tertiary"
                ? "bg-tertiary"
                : "bg-slate-400"
            )}
          />
        </div>
      </div>
    </motion.div>
  );
}

function MealCard({
  meal,
}: Readonly<{
  meal: MealPlanItemResponse;
}>) {
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const mouseXSpring = useSpring(x);
  const mouseYSpring = useSpring(y);

  const rotateX = useTransform(mouseYSpring, [-0.5, 0.5], ["8deg", "-8deg"]);
  const rotateY = useTransform(mouseXSpring, [-0.5, 0.5], ["-8deg", "8deg"]);

  const handleMouseMove = (event: React.MouseEvent<HTMLDivElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;
    const xPct = mouseX / width - 0.5;
    const yPct = mouseY / height - 0.5;
    x.set(xPct);
    y.set(yPct);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.98 }}
      whileInView={{ opacity: 1, scale: 1 }}
      viewport={{ once: true }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        rotateX,
        rotateY,
        transformStyle: "preserve-3d",
      }}
      className="group relative overflow-hidden rounded-lg border border-primary/5 bg-[rgba(46,53,69,0.4)] shadow-[0_8px_32px_0_rgba(0,0,0,0.37)] backdrop-blur-[40px] transition-all duration-300 hover:border-primary/20"
    >
      <div
        className="relative h-48 w-full overflow-hidden"
        style={{ transform: "translateZ(40px)" }}
      >
        <img
          src={mealImages[meal.meal_slot]}
          alt={meal.food_name_snapshot}
          className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
          referrerPolicy="no-referrer"
        />
        <div className="absolute left-4 top-4 rounded-sm bg-primary/90 px-3 py-1 text-[9px] font-black uppercase leading-none tracking-widest text-on-primary shadow-lg backdrop-blur-md">
          {formatMealTime(meal.meal_slot)}
        </div>
        <div className="absolute inset-0 bg-gradient-to-t from-background/90 via-background/20 to-transparent" />
        <div className="absolute bottom-3 left-5" style={{ transform: "translateZ(25px)" }}>
          <h3 className="font-headline text-xl font-black tracking-tight text-white">
            {meal.food_name_snapshot}
          </h3>
        </div>
      </div>

      <div className="p-5" style={{ transform: "translateZ(15px)" }}>
        <div className="mb-6 flex items-center justify-between">
          <div className="flex flex-col">
            <span className="mb-0.5 text-[9px] font-black uppercase tracking-widest text-slate-500">
              Calories
            </span>
            <span className="text-xl font-black text-on-surface">
              {Math.round(meal.calories)}
            </span>
          </div>

          <div className="flex gap-3">
            {[
              { label: "P", val: `${Math.round(meal.protein_g)}g`, col: "text-primary" },
              { label: "C", val: `${Math.round(meal.carbs_g)}g`, col: "text-secondary" },
              { label: "F", val: `${Math.round(meal.fat_g)}g`, col: "text-tertiary" },
            ].map((macro) => (
              <div key={macro.label} className="text-center transition-transform group-hover:scale-105">
                <span className={cn("block text-[9px] font-black", macro.col)}>
                  {macro.label}
                </span>
                <span className="text-xs font-bold">{macro.val}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-3 gap-2">
          <button
            type="button"
            className="flex items-center justify-center gap-1.5 rounded bg-surface-container-highest/40 py-2 text-[9px] font-black uppercase tracking-widest transition-all hover:bg-surface-bright"
          >
            <RefreshCw className="h-3 w-3" />
            Swap
          </button>
          <button
            type="button"
            className="flex items-center justify-center gap-1.5 rounded bg-surface-container-highest/40 py-2 text-[9px] font-black uppercase tracking-widest transition-all hover:bg-surface-bright"
          >
            <BookOpen className="h-3 w-3" />
            Recipe
          </button>
          <button
            type="button"
            className="flex items-center justify-center gap-1.5 rounded bg-primary py-2 text-[9px] font-black uppercase tracking-widest text-on-primary shadow-lg transition-all hover:bg-primary-container"
          >
            <CheckCircle2 className="h-3 w-3" />
            Log
          </button>
        </div>
      </div>
    </motion.div>
  );
}

function deriveInventoryItems(plan: MealPlanResponse | null): InventoryItem[] {
  if (!plan) {
    return [];
  }

  const grouped = new Map<string, { amount: number }>();

  for (const item of plan.items) {
    const key = item.food_name_snapshot;
    const existing = grouped.get(key);

    if (existing) {
      existing.amount += item.planned_grams;
    } else {
      grouped.set(key, { amount: item.planned_grams });
    }
  }

  return Array.from(grouped.entries()).map(([name, entry], index) => ({
    id: `${name}-${index}`,
    name,
    amount: `${Math.round(entry.amount)}g`,
    completed: index === 0,
  }));
}

function InventorySidebar({
  items,
}: Readonly<{
  items: InventoryItem[];
}>) {
  const [localItems, setLocalItems] = useState(items);

  useEffect(() => {
    setLocalItems(items);
  }, [items]);

  const toggleItem = (id: string) => {
    setLocalItems((current) =>
      current.map((item) =>
        item.id === id ? { ...item, completed: !item.completed } : item
      )
    );
  };

  return (
    <aside className="fixed right-0 top-20 hidden h-[calc(100vh-5rem)] w-80 flex-col gap-6 border-l border-primary/10 bg-surface-container-low/40 p-8 backdrop-blur-3xl lg:flex">
      <div className="mb-4 flex items-center gap-4">
        <div className="flex h-14 w-14 items-center justify-center rounded-lg border border-primary/20 bg-primary/10 shadow-[0_0_15px_rgba(78,222,163,0.15)]">
          <ShoppingCart className="h-8 w-8 text-primary" />
        </div>
        <div>
          <h2 className="mb-1 font-headline text-2xl font-black leading-none text-white">
            Pro Visions
          </h2>
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-400">
            Weekly Inventory
          </p>
        </div>
      </div>

      <div className="no-scrollbar flex flex-1 flex-col gap-3 overflow-y-auto">
        <AnimatePresence>
          {localItems.length > 0 ? (
            localItems.map((item) => (
              <motion.div
                key={item.id}
                layout
                onClick={() => toggleItem(item.id)}
                className={cn(
                  "group flex cursor-pointer items-center gap-4 rounded-lg border border-transparent p-5 transition-all",
                  item.completed
                    ? "border-primary/10 opacity-50"
                    : "bg-[rgba(46,53,69,0.4)] hover:border-primary/30"
                )}
              >
                <div
                  className={cn(
                    "flex h-6 w-6 items-center justify-center rounded-full border-2 transition-all",
                    item.completed
                      ? "border-primary bg-primary"
                      : "border-primary/30 group-hover:bg-primary/10"
                  )}
                >
                  {item.completed ? <Check className="h-3 w-3 text-white" /> : null}
                </div>

                <div className="flex-1">
                  <span
                    className={cn(
                      "block text-sm font-bold",
                      item.completed
                        ? "text-slate-500 line-through"
                        : "text-on-surface"
                    )}
                  >
                    {item.name}
                  </span>
                  <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">
                    {item.amount}
                  </span>
                </div>
              </motion.div>
            ))
          ) : (
            <div className="rounded-lg bg-[rgba(46,53,69,0.35)] p-5 text-sm font-medium text-slate-400">
              Generate a plan for a selected day to populate this inventory panel.
            </div>
          )}
        </AnimatePresence>
      </div>

      <div className="mt-auto border-t border-primary/10 pt-6">
        <button
          type="button"
          className="w-full rounded-lg bg-primary py-5 text-sm font-black text-on-primary shadow-[0_10px_30px_rgba(78,222,163,0.3)] transition-all hover:scale-[1.02] active:scale-95"
        >
          Fulfill on Instacart
        </button>
      </div>
    </aside>
  );
}

export default function MealPlansPage() {
  const router = useRouter();
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [hydrated, setHydrated] = useState(false);
  const [selectedDate, setSelectedDate] = useState<string>("");

  useEffect(() => {
    setAccessToken(getAccessToken());
    setHydrated(true);
  }, []);

  const mealPlansQuery = useMealPlansQuery(accessToken);
  const generateMutation = useGenerateMealPlanMutation();

  useEffect(() => {
    if (!hydrated) {
      return;
    }

    if (!accessToken) {
      router.replace("/login");
    }
  }, [accessToken, hydrated, router]);

  useEffect(() => {
    if (!mealPlansQuery.data) {
      return;
    }

    if (!mealPlansQuery.data.profile || !mealPlansQuery.data.currentGoal) {
      router.replace("/welcome");
    }
  }, [mealPlansQuery.data, router]);

  const weekDays = useMemo(() => {
    const monday = startOfWeek(new Date());
    return dayNames.map((dayName, index) => {
      const date = addDays(monday, index);
      return {
        label: dayName,
        isoDate: toIsoDate(date),
      };
    });
  }, []);

  useEffect(() => {
    if (selectedDate) {
      return;
    }

    const todayIso = toIsoDate(new Date());
    setSelectedDate(todayIso);
  }, [selectedDate]);

  const sortedPlans = useMemo(() => {
    if (!mealPlansQuery.data) {
      return [];
    }

    return [...mealPlansQuery.data.mealPlans].sort((a, b) =>
      a.plan_date.localeCompare(b.plan_date)
    );
  }, [mealPlansQuery.data]);

  const selectedPlan = useMemo(() => {
    return sortedPlans.find((plan) => plan.plan_date === selectedDate) ?? null;
  }, [selectedDate, sortedPlans]);

  const currentWeekRange = useMemo(() => {
    const first = weekDays[0]?.isoDate;
    const last = weekDays[6]?.isoDate;

    if (!first || !last) {
      return "";
    }

    return formatRange(first, last);
  }, [weekDays]);

  const macroStats = useMemo(() => {
    if (!mealPlansQuery.data) {
      return [] as MacroInfo[];
    }

    return deriveMacroStats(mealPlansQuery.data);
  }, [mealPlansQuery.data]);

  const weeklyAdherence = useMemo(() => {
    const snapshots = mealPlansQuery.data?.snapshots ?? [];
    if (snapshots.length === 0) {
      return 0;
    }

    const average =
      snapshots.reduce((sum, snapshot) => sum + snapshot.overall_adherence_score, 0) /
      snapshots.length;

    return clampPercentage(average);
  }, [mealPlansQuery.data]);

  const completionDays = useMemo(() => {
    const snapshotMap = new Map(
      (mealPlansQuery.data?.snapshots ?? []).map((snapshot) => [
        snapshot.snapshot_date,
        snapshot.overall_adherence_score,
      ])
    );

    return weekDays.map((day) => ({
      label: day.label.slice(0, 1),
      complete: (snapshotMap.get(day.isoDate) ?? 0) >= 70,
    }));
  }, [mealPlansQuery.data, weekDays]);

  const inventoryItems = useMemo(
    () => deriveInventoryItems(selectedPlan),
    [selectedPlan]
  );

  const mealsForDay = useMemo(() => {
    if (!selectedPlan) {
      return [];
    }

    const order: MealSlot[] = ["breakfast", "lunch", "dinner", "snack"];
    return order
      .map((slot) => selectedPlan.items.find((item) => item.meal_slot === slot))
      .filter((item): item is MealPlanItemResponse => Boolean(item));
  }, [selectedPlan]);

  const handleGenerate = () => {
    if (!accessToken || !selectedDate) {
      return;
    }

    generateMutation.mutate({
      accessToken,
      payload: {
        plan_date: selectedDate,
        notes: null,
        meal_slots: ["breakfast", "lunch", "dinner", "snack"],
        preferred_food_item_ids: [],
        max_items_per_slot: 1,
      },
    });
  };

  if (!hydrated) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background">
        <LoadingState label="Preparing your meals..." className="text-primary" />
      </main>
    );
  }

  if (!accessToken) {
    return null;
  }

  if (mealPlansQuery.isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background">
        <LoadingState label="Loading your meal strategy..." className="text-primary" />
      </main>
    );
  }

  if (mealPlansQuery.isError) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background px-6">
        <ErrorState message={mealPlansQuery.error.message} />
      </main>
    );
  }

  if (
    !mealPlansQuery.data ||
    !mealPlansQuery.data.profile ||
    !mealPlansQuery.data.currentGoal
  ) {
    return null;
  }

  return (
    <div className="relative min-h-screen overflow-x-hidden bg-background">
      <main className="relative z-10 mx-auto max-w-7xl px-8 pb-20 pt-8 lg:mr-80">
        <section className="mb-10 flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="flex-1"
          >
            <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center">
              <div className="flex items-center gap-3 rounded-lg border border-primary/20 bg-[#102420] px-4 py-2 shadow-[0_10px_30px_rgba(78,222,163,0.1)]">
                <div className="relative flex h-2.5 w-2.5 items-center justify-center">
                  <div className="h-2 w-2 rounded-full bg-primary" />
                  <div className="absolute inset-0 h-full w-full animate-ping rounded-full bg-primary/40" />
                </div>
                <div className="flex flex-col leading-tight">
                  <span className="text-[9px] font-black tracking-[0.2em] text-primary/60">
                    ELITE
                  </span>
                  <span className="text-[11px] font-black tracking-[0.1em] text-primary">
                    STATUS
                  </span>
                </div>
              </div>

              <span className="max-w-sm border-l-2 border-primary/20 pl-4 text-sm font-semibold italic leading-tight text-primary/80">
                "Discipline is the bridge between goals and accomplishment."
              </span>
            </div>

            <motion.h1
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1, ease: "circOut" }}
              className="mb-4 bg-gradient-to-br from-white via-white to-slate-500 bg-clip-text font-headline text-4xl font-black leading-none tracking-tighter text-transparent md:text-6xl"
            >
              This Week&apos;s Strategy
            </motion.h1>

            <div className="flex items-center gap-3">
              <div className="h-px w-10 bg-primary/30" />
              <p className="flex items-center gap-2 text-lg font-medium text-slate-400">
                <Calendar className="h-4 w-4 text-primary" />
                {currentWeekRange} • Peak Performance Plan
              </p>
            </div>
          </motion.div>

          <div className="flex flex-col gap-3 sm:flex-row lg:mb-2">
            <motion.button
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
              type="button"
              onClick={() => router.push("/goals")}
              className="rounded-lg border border-white/5 bg-[rgba(46,53,69,0.4)] px-6 py-3 text-xs font-black text-on-surface shadow-[0_8px_32px_0_rgba(0,0,0,0.37)] backdrop-blur-[40px] transition-all hover:bg-surface-bright"
            >
              Adjust Goals
            </motion.button>

            <motion.button
              whileHover={{
                scale: 1.05,
                y: -2,
                boxShadow: "0 20px 50px rgba(78, 222, 163, 0.4)",
              }}
              whileTap={{ scale: 0.95 }}
              type="button"
              onClick={handleGenerate}
              disabled={generateMutation.isPending}
              className="flex items-center justify-center gap-2 rounded-lg bg-primary px-8 py-3 text-xs font-black text-on-primary shadow-[0_10px_40px_rgba(78,222,163,0.3)] transition-all disabled:opacity-70"
            >
              <Sparkles className="h-3.5 w-3.5" />
              {generateMutation.isPending ? "Regenerating..." : "Regenerate Plan"}
            </motion.button>
          </div>
        </section>

        <section className="mb-14 grid grid-cols-2 gap-5 md:grid-cols-4">
          {macroStats.map((stat) => (
            <MacroStatCard key={stat.label} stat={stat} />
          ))}
        </section>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-10 flex items-center justify-between rounded-lg border border-primary/5 bg-[rgba(46,53,69,0.4)] px-6 py-4 shadow-[0_8px_32px_0_rgba(0,0,0,0.37)] backdrop-blur-[40px]"
        >
          <div className="flex items-center gap-4">
            <div className="relative flex h-12 w-12 items-center justify-center">
              <svg className="absolute inset-0 h-full w-full -rotate-90" viewBox="0 0 48 48">
                <circle
                  className="text-primary/10"
                  cx="24"
                  cy="24"
                  r="20"
                  fill="transparent"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <motion.circle
                  initial={{ strokeDashoffset: 125.6 }}
                  animate={{
                    strokeDashoffset: 125.6 - (125.6 * weeklyAdherence) / 100,
                  }}
                  transition={{ duration: 2, ease: "circOut", delay: 0.5 }}
                  className="text-primary"
                  cx="24"
                  cy="24"
                  r="20"
                  fill="transparent"
                  stroke="currentColor"
                  strokeWidth="4"
                  strokeDasharray="125.6"
                  strokeLinecap="round"
                />
              </svg>
              <span className="text-xs font-black text-on-surface">
                {weeklyAdherence}%
              </span>
            </div>

            <div>
              <h4 className="font-headline text-sm font-bold">
                Weekly Adherence
              </h4>
              <p className="text-xs text-slate-400">
                You&apos;re on track for your current nutrition target. Keep it up!
              </p>
            </div>
          </div>

          <div className="flex -space-x-2">
            {completionDays.slice(0, 5).map((day, index) => (
              <motion.div
                key={`${day.label}-${index}`}
                whileHover={{ y: -4, scale: 1.1 }}
                className={cn(
                  "flex h-8 w-8 cursor-help items-center justify-center rounded-full border-2 border-background text-[10px] font-bold",
                  day.complete
                    ? "bg-primary/20 text-primary"
                    : "bg-surface-container-highest text-slate-500"
                )}
              >
                {day.label}
              </motion.div>
            ))}
          </div>
        </motion.div>

        <div className="relative mb-10 group">
          <div className="no-scrollbar flex gap-3 overflow-x-auto pb-4">
            {weekDays.map((day) => (
              <button
                key={day.isoDate}
                type="button"
                onClick={() => setSelectedDate(day.isoDate)}
                className={cn(
                  "shrink-0 rounded-lg px-8 py-3 text-sm font-black transition-all",
                  selectedDate === day.isoDate
                    ? "bg-primary text-on-primary shadow-[0_10px_20px_rgba(78,222,163,0.2)]"
                    : "border border-white/5 bg-[rgba(46,53,69,0.4)] text-slate-400 shadow-[0_8px_32px_0_rgba(0,0,0,0.37)] backdrop-blur-[40px] hover:text-on-surface"
                )}
              >
                {day.label}
              </button>
            ))}
          </div>
        </div>

        {generateMutation.isError ? (
          <div className="mb-8 rounded-lg bg-[#ffb4ab]/10 px-4 py-3 text-sm text-[#ffb4ab]">
            {generateMutation.error.message}
          </div>
        ) : null}

        {selectedPlan ? (
          <section className="grid grid-cols-1 gap-8 xl:grid-cols-2 2xl:grid-cols-2">
            {mealsForDay.map((meal) => (
              <MealCard key={meal.id} meal={meal} />
            ))}
          </section>
        ) : (
          <section className="rounded-2xl border border-primary/10 bg-[rgba(46,53,69,0.3)] p-10 backdrop-blur-2xl">
            <h3 className="font-headline text-2xl font-black text-white">
              No plan for this day yet
            </h3>
            <p className="mt-3 max-w-xl text-sm leading-relaxed text-slate-400">
              Generate a rule-based meal plan for the selected day and this screen
              will populate automatically from your real FastAPI meal plan endpoint.
            </p>
            <button
              type="button"
              onClick={handleGenerate}
              disabled={generateMutation.isPending}
              className="mt-6 inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-xs font-black text-on-primary shadow-[0_10px_30px_rgba(78,222,163,0.25)] disabled:opacity-70"
            >
              <Sparkles className="h-4 w-4" />
              {generateMutation.isPending ? "Generating..." : "Generate for This Day"}
            </button>
          </section>
        )}
      </main>

      <InventorySidebar items={inventoryItems} />

      <style jsx global>{`
        .no-scrollbar::-webkit-scrollbar {
          display: none;
        }
        .no-scrollbar {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
    </div>
  );
}