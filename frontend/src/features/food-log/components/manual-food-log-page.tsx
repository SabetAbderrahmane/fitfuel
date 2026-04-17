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
  Activity,
  Bot,
  Camera,
  Check,
  Plus,
  Search,
  Sparkles,
  Zap,
} from "lucide-react";

import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { useCreateFoodLogMutation } from "@/features/food-log/hooks/use-create-food-log-mutation";
import { useFoodLogPageQuery } from "@/features/food-log/hooks/use-food-log-page-query";
import { useFoodSearchQuery } from "@/features/food-log/hooks/use-food-search-query";
import type {
  CreateFoodLogPreview,
  FoodItemResponse,
  MealType,
  SelectedFoodItem,
} from "@/features/food-log/types/food-log.types";
import { cn } from "@/lib/utils/cn";

type VaultItem = {
  id: string;
  title: string;
  subtitle: string;
  image: string;
  food?: FoodItemResponse;
  disabled?: boolean;
};

const fallbackVaultItems: VaultItem[] = [
  {
    id: "fallback-1",
    title: "Quinoa Power Bowl",
    subtitle: "420 KCAL • 18G P",
    image:
      "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?q=80&w=300&auto=format&fit=crop",
    disabled: true,
  },
  {
    id: "fallback-2",
    title: "Whey Protein Shake",
    subtitle: "150 KCAL • 25G P",
    image:
      "https://images.unsplash.com/photo-1579722821273-0f6c7d44362f?q=80&w=300&auto=format&fit=crop",
    disabled: true,
  },
  {
    id: "fallback-3",
    title: "Whole Wheat Pasta",
    subtitle: "320 KCAL • 56G C",
    image:
      "https://images.unsplash.com/photo-1551024601-bec78aea704b?q=80&w=300&auto=format&fit=crop",
    disabled: true,
  },
];

const searchPreviewImages = [
  "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?q=80&w=300&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1547592180-85f173990554?q=80&w=300&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1551024601-bec78aea704b?q=80&w=300&auto=format&fit=crop",
] as const;

const mealTypeOptions: Array<{ id: MealType; label: string }> = [
  { id: "breakfast", label: "Breakfast" },
  { id: "lunch", label: "Lunch" },
  { id: "dinner", label: "Dinner" },
  { id: "snack", label: "Snack" },
];

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

function getNutritionValues(food: FoodItemResponse, grams: number | null) {
  const actualGrams = grams ?? food.default_serving_size_g ?? 100;
  const factor = actualGrams / 100;
  const nutrition = food.nutrition_fact;

  return {
    grams: actualGrams,
    calories: Math.round((nutrition?.calories_per_100g ?? 0) * factor),
    protein:
      Math.round((nutrition?.protein_g_per_100g ?? 0) * factor * 10) / 10,
    carbs: Math.round((nutrition?.carbs_g_per_100g ?? 0) * factor * 10) / 10,
    fat: Math.round((nutrition?.fat_g_per_100g ?? 0) * factor * 10) / 10,
  };
}

function FloatingDecoration() {
  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage:
            'url("data:image/svg+xml,%3Csvg viewBox=\'0 0 200 200\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noiseFilter\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.65\' numOctaves=\'3\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23noiseFilter)\'/%3E%3C/svg%3E")',
        }}
      />

      {[...Array(6)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute h-64 w-64 rounded-full"
          style={{
            background:
              "radial-gradient(circle, rgba(78, 222, 163, 0.05) 0%, transparent 70%)",
            left: `${(i * 17) % 100}%`,
            top: `${(i * 23) % 100}%`,
          }}
          animate={{
            x: [0, 50, -50, 0],
            y: [0, -50, 50, 0],
            scale: [1, 1.2, 0.8, 1],
          }}
          transition={{
            duration: 15 + i * 2,
            repeat: Infinity,
            ease: "linear",
          }}
        />
      ))}
    </div>
  );
}

function QuickLogModal({
  food,
  open,
  onClose,
  onConfirm,
  isPending,
}: Readonly<{
  food: FoodItemResponse | null;
  open: boolean;
  onClose: () => void;
  onConfirm: (values: {
    mealType: MealType;
    loggedForDate: string;
    grams: number;
  }) => void;
  isPending: boolean;
}>) {
  const [mealType, setMealType] = useState<MealType>("breakfast");
  const [loggedForDate, setLoggedForDate] = useState(todayIso());
  const [grams, setGrams] = useState<number>(100);

  useEffect(() => {
    if (!food) {
      return;
    }

    setMealType("breakfast");
    setLoggedForDate(todayIso());
    setGrams(Math.round(food.default_serving_size_g ?? 100));
  }, [food]);

  if (!open || !food) {
    return null;
  }

  const nutrition = getNutritionValues(food, grams);

  return (
    <AnimatePresence>
      <motion.button
        key="quick-log-backdrop"
        type="button"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm"
      />

      <motion.div
        key="quick-log-panel"
        initial={{ opacity: 0, scale: 0.96, y: 18 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.98, y: 8 }}
        transition={{ duration: 0.2, ease: "easeOut" }}
        className="fixed inset-0 z-[110] flex items-center justify-center px-4"
      >
        <div className="w-full max-w-lg rounded-[1.75rem] border border-primary/10 bg-[rgba(20,27,43,0.82)] p-6 shadow-[0_20px_60px_rgba(0,0,0,0.45)] backdrop-blur-[40px]">
          <div className="mb-5">
            <div className="text-[10px] font-black uppercase tracking-[0.24em] text-primary">
              Quick Add
            </div>
            <h3 className="mt-2 font-headline text-3xl font-black tracking-tight text-white">
              {food.name}
            </h3>
            <p className="mt-1 text-sm text-slate-400">
              Confirm the meal type and grams, then log it instantly.
            </p>
          </div>

          <div className="mb-5 grid grid-cols-1 gap-4 md:grid-cols-2">
            <label className="space-y-2">
              <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">
                Date
              </span>
              <input
                type="date"
                value={loggedForDate}
                onChange={(event) => setLoggedForDate(event.target.value)}
                className="w-full rounded-xl bg-surface-container-highest/30 px-4 py-3 text-sm font-semibold text-white outline-none"
              />
            </label>

            <label className="space-y-2">
              <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">
                Grams
              </span>
              <input
                type="number"
                min="1"
                step="1"
                value={grams}
                onChange={(event) =>
                  setGrams(Math.max(1, Number(event.target.value) || 1))
                }
                className="w-full rounded-xl bg-surface-container-highest/30 px-4 py-3 text-sm font-semibold text-white outline-none"
              />
            </label>
          </div>

          <div className="mb-5 flex flex-wrap gap-2">
            {mealTypeOptions.map((option) => (
              <button
                key={option.id}
                type="button"
                onClick={() => setMealType(option.id)}
                className={cn(
                  "rounded-full px-4 py-2 text-[10px] font-black uppercase tracking-widest transition-all",
                  mealType === option.id
                    ? "bg-primary text-on-primary"
                    : "bg-surface-container-highest/30 text-slate-400"
                )}
              >
                {option.label}
              </button>
            ))}
          </div>

          <div className="mb-6 grid grid-cols-4 gap-3">
            <div className="rounded-xl bg-surface-container-highest/20 p-3">
              <div className="text-[9px] font-black uppercase tracking-widest text-primary">
                kcal
              </div>
              <div className="mt-1 text-lg font-black text-white">
                {nutrition.calories}
              </div>
            </div>
            <div className="rounded-xl bg-surface-container-highest/20 p-3">
              <div className="text-[9px] font-black uppercase tracking-widest text-primary">
                P
              </div>
              <div className="mt-1 text-lg font-black text-white">
                {nutrition.protein}g
              </div>
            </div>
            <div className="rounded-xl bg-surface-container-highest/20 p-3">
              <div className="text-[9px] font-black uppercase tracking-widest text-secondary">
                C
              </div>
              <div className="mt-1 text-lg font-black text-white">
                {nutrition.carbs}g
              </div>
            </div>
            <div className="rounded-xl bg-surface-container-highest/20 p-3">
              <div className="text-[9px] font-black uppercase tracking-widest text-slate-300">
                F
              </div>
              <div className="mt-1 text-lg font-black text-white">
                {nutrition.fat}g
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 rounded-xl border border-white/5 bg-[rgba(46,53,69,0.4)] px-5 py-4 text-sm font-black text-white"
            >
              Cancel
            </button>

            <button
              type="button"
              onClick={() =>
                onConfirm({
                  mealType,
                  loggedForDate,
                  grams,
                })
              }
              disabled={isPending}
              className="flex-1 rounded-xl bg-primary px-5 py-4 text-sm font-black text-on-primary shadow-[0_10px_30px_rgba(78,222,163,0.25)] disabled:opacity-70"
            >
              {isPending ? "Logging..." : "Confirm Log"}
            </button>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}

function SearchVaultRow({
  item,
  onAdd,
}: Readonly<{
  item: VaultItem;
  onAdd?: (food: FoodItemResponse) => void;
}>) {
  const food = item.food;

  return (
    <div className="group flex items-center justify-between gap-3 py-4">
      <div className="flex min-w-0 items-center gap-4">
        <img
          src={item.image}
          alt={item.title}
          className="h-[4.4rem] w-[4.4rem] rounded-[1.25rem] object-cover grayscale"
          referrerPolicy="no-referrer"
        />

        <div className="min-w-0">
          <div className="line-clamp-2 font-headline text-[1.55rem] font-black leading-[0.95] tracking-tight text-white">
            {item.title}
          </div>
          <div className="mt-1 text-[11px] font-black uppercase tracking-[0.08em] text-slate-400">
            {item.subtitle}
          </div>
        </div>
      </div>

      {food && onAdd ? (
        <button
          type="button"
          onClick={() => onAdd(food)}
          className="shrink-0 rounded-full border border-white/10 p-2.5 text-slate-400 transition-all hover:border-primary/30 hover:text-primary"
        >
          <Plus className="h-5 w-5" />
        </button>
      ) : (
        <div className="shrink-0 rounded-full border border-white/10 p-2.5 text-slate-700">
          <Plus className="h-5 w-5" />
        </div>
      )}
    </div>
  );
}
function HeroVisionCard({
  onScan,
}: Readonly<{
  onScan: () => void;
}>) {
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const springX = useSpring(x, { stiffness: 120, damping: 18 });
  const springY = useSpring(y, { stiffness: 120, damping: 18 });

  const rotateX = useTransform(springY, [-0.5, 0.5], ["6deg", "-6deg"]);
  const rotateY = useTransform(springX, [-0.5, 0.5], ["-6deg", "6deg"]);

  const handleMouseMove = (event: React.MouseEvent<HTMLDivElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const px = (event.clientX - rect.left) / rect.width - 0.5;
    const py = (event.clientY - rect.top) / rect.height - 0.5;

    x.set(px);
    y.set(py);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, delay: 0.12 }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        rotateX,
        rotateY,
        transformStyle: "preserve-3d",
      }}
      className="relative h-[28.5rem] overflow-hidden rounded-[2.25rem] border border-primary/10 bg-[rgba(20,27,43,0.45)] shadow-[0_10px_40px_rgba(0,0,0,0.35)] backdrop-blur-[40px]"
    >
      <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(12,19,34,0.08),rgba(78,222,163,0.03),rgba(12,19,34,0))]" />

      <div className="relative z-10 flex h-full flex-col items-center justify-center px-10 text-center">
        <motion.div
          animate={{ y: [0, -9, 0] }}
          transition={{ duration: 3.4, repeat: Infinity, ease: "easeInOut" }}
          className="mb-8 flex h-[6.4rem] w-[6.4rem] items-center justify-center rounded-[2rem] border border-primary/20 bg-primary/5 shadow-[0_0_30px_rgba(78,222,163,0.08)]"
          style={{ transform: "translateZ(36px)" }}
        >
          <Camera className="h-12 w-12 text-primary" />
        </motion.div>

        <h2
          className="font-headline text-[3.55rem] font-black tracking-tight text-white"
          style={{ transform: "translateZ(42px)" }}
        >
          Vision AI Ready
        </h2>

        <p
          className="mt-5 max-w-[31rem] text-[1.15rem] leading-[1.7] text-slate-400"
          style={{ transform: "translateZ(28px)" }}
        >
          Point your camera at any meal. Our neural engine handles the rest.
        </p>

        <motion.button
          type="button"
          onClick={onScan}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          animate={{
            boxShadow: [
              "0 14px 40px rgba(78,222,163,0.24)",
              "0 18px 48px rgba(78,222,163,0.38)",
              "0 14px 40px rgba(78,222,163,0.24)",
            ],
          }}
          transition={{
            boxShadow: { duration: 2.4, repeat: Infinity, ease: "easeInOut" },
          }}
          className="mt-10 rounded-full bg-primary px-16 py-6 text-[1rem] font-black uppercase tracking-[0.12em] text-on-primary"
          style={{ transform: "translateZ(48px)" }}
        >
          Initiate Smart Scan
        </motion.button>
      </div>

      <motion.div
        animate={{ y: [0, -10, 0], rotate: [0, 1.5, 0], scale: [1, 1.025, 1] }}
        transition={{ duration: 4.2, repeat: Infinity, ease: "easeInOut" }}
        className="pointer-events-none absolute bottom-[-2.1rem] right-[-1.6rem] z-0 h-[19.5rem] w-[19.5rem] rounded-full bg-white/8"
        style={{ transform: "translateZ(60px)" }}
      >
        <div className="h-full w-full overflow-hidden rounded-full">
          <img
            src="https://images.unsplash.com/photo-1512621776951-a57141f2eefd?q=80&w=1200&auto=format&fit=crop"
            alt="Meal bowl"
            className="h-full w-full object-cover grayscale brightness-[0.9]"
            referrerPolicy="no-referrer"
          />
        </div>
      </motion.div>
    </motion.div>
  );
}

export function ManualFoodLogPage({
  accessToken,
}: Readonly<{
  accessToken: string;
}>) {
  const router = useRouter();
  const pageQuery = useFoodLogPageQuery(accessToken);
  const [search, setSearch] = useState("");
  const [selectedFood, setSelectedFood] = useState<FoodItemResponse | null>(null);
  const searchQuery = useFoodSearchQuery(accessToken, search);
  const createMutation = useCreateFoodLogMutation();

  const vaultItems = useMemo<VaultItem[]>(() => {
    if (search.trim()) {
      return (searchQuery.data ?? []).slice(0, 3).map((food, index) => {
        const nutrition = getNutritionValues(food, 100);

        return {
          id: food.id,
          title: food.name,
          subtitle: `${nutrition.calories} KCAL • ${Math.round(
            nutrition.protein
          )}G P`,
          image: searchPreviewImages[index % searchPreviewImages.length],
          food,
        };
      });
    }

    const recentLogs = pageQuery.data?.recentLogs ?? [];

    const mappedRecent = recentLogs
      .flatMap((log) =>
        log.items.map((item, index) => ({
          id: `${log.id}-${item.id}`,
          title: item.food_name_snapshot,
          subtitle: `${Math.round(item.calories)} KCAL • ${Math.round(
            item.protein_g
          )}G P`,
          image: searchPreviewImages[index % searchPreviewImages.length],
          disabled: true,
        }))
      )
      .slice(0, 3);

    return mappedRecent.length > 0 ? mappedRecent : fallbackVaultItems;
  }, [pageQuery.data?.recentLogs, search, searchQuery.data]);

  const chainActivationDays = useMemo(() => {
    const dates = new Set(
      (pageQuery.data?.recentLogs ?? []).map((log) => log.logged_for_date)
    );
    return dates.size > 0 ? dates.size : 12;
  }, [pageQuery.data?.recentLogs]);

  const metrics = useMemo(() => {
    const goal = pageQuery.data?.currentGoal;
    const snapshot = pageQuery.data?.latestSnapshot;

    const energyValue = snapshot?.consumed_calories ?? goal?.target_calories ?? 1420;
    const proteinValue =
      snapshot?.consumed_protein_g ?? goal?.target_protein_g ?? 82;
    const carbsValue = snapshot?.consumed_carbs_g ?? goal?.target_carbs_g ?? 110;
    const fatValue = snapshot?.consumed_fat_g ?? goal?.target_fat_g ?? 35;

    return [
      {
        label: "ENERGY BALANCE",
        value: Math.round(energyValue).toLocaleString(),
        unit: "KCAL",
        width: Math.max(24, Math.min(snapshot?.calorie_adherence_pct ?? 36, 100)),
        barClass: "bg-primary",
      },
      {
        label: "MUSCLE SYNTHESIS",
        value: Math.round(proteinValue).toLocaleString(),
        unit: "GRAMS",
        width: Math.max(24, Math.min(snapshot?.protein_adherence_pct ?? 48, 100)),
        barClass: "bg-primary",
      },
      {
        label: "GLYCOGEN RESERVES",
        value: Math.round(carbsValue).toLocaleString(),
        unit: "GRAMS",
        width: Math.max(24, Math.min(snapshot?.carbs_adherence_pct ?? 67, 100)),
        barClass: "bg-secondary",
      },
      {
        label: "CELLULAR FUEL",
        value: Math.round(fatValue).toLocaleString(),
        unit: "GRAMS",
        width: Math.max(24, Math.min(snapshot?.fat_adherence_pct ?? 42, 100)),
        barClass: "bg-tertiary",
      },
    ];
  }, [pageQuery.data]);

  const handleQuickAdd = (food: FoodItemResponse) => {
    setSelectedFood(food);
  };

  const confirmQuickAdd = (values: {
    mealType: MealType;
    loggedForDate: string;
    grams: number;
  }) => {
    if (!selectedFood) {
      return;
    }

    const previewItem: SelectedFoodItem = {
      food: selectedFood,
      quantity: 1,
      grams: values.grams,
    };

    const preview: CreateFoodLogPreview = {
      loggedForDate: values.loggedForDate,
      mealType: values.mealType,
      notes: null,
      selectedItems: [previewItem],
    };

    createMutation.mutate(
      {
        accessToken,
        payload: {
          logged_for_date: values.loggedForDate,
          meal_type: values.mealType,
          notes: null,
          items: [
            {
              food_item_id: selectedFood.id,
              quantity: 1,
              grams: values.grams,
            },
          ],
        },
        preview,
      },
      {
        onSuccess: () => {
          setSelectedFood(null);
        },
      }
    );
  };

  if (pageQuery.isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background">
        <LoadingState
          label="Loading your food logging workspace..."
          className="text-primary"
        />
      </main>
    );
  }

  if (pageQuery.isError) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background px-6">
        <ErrorState message={pageQuery.error.message} />
      </main>
    );
  }

  return (
    <div className="relative min-h-screen overflow-x-hidden bg-background">
      <FloatingDecoration />

      <main className="relative z-10 mx-auto max-w-[1460px] px-8 pb-24 pt-6">
        <section className="mb-9">
          <motion.h1
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: "easeOut" }}
            className="font-headline text-[5.15rem] font-black leading-[0.9] tracking-tighter text-white"
          >
            Log Your <span className="text-primary">Fuel</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.08, ease: "easeOut" }}
            className="mt-4 max-w-[62rem] text-[1.25rem] leading-[1.65] text-slate-300"
          >
            Harnessing Advanced Neural Vision to decode your nutrition. Precision
            tracking, zero friction.
          </motion.p>
        </section>

        <section className="grid grid-cols-1 gap-10 xl:grid-cols-[minmax(0,1fr)_21.5rem]">
          <div className="space-y-10">
            <HeroVisionCard onScan={() => router.push("/photo-estimator")} />

            <motion.div
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.2 }}
              className="rounded-[2rem] border border-primary/10 bg-[rgba(20,27,43,0.45)] px-9 py-7 shadow-[0_10px_40px_rgba(0,0,0,0.35)] backdrop-blur-[40px]"
            >
              <div className="flex flex-col gap-5 xl:flex-row xl:items-center xl:justify-between">
                <div>
                  <div className="flex items-center gap-2 text-[12px] font-black uppercase tracking-[0.28em] text-primary">
                    <Sparkles className="h-4 w-4" />
                    Processing Engine
                  </div>
                  <p className="mt-2 text-[1.55rem] italic leading-none text-slate-400">
                    Vectorizing nutritional data...
                  </p>
                </div>

                <div className="hidden items-center gap-9 xl:flex">
                  {["CALORIES", "PROTEIN", "MACROS"].map((item) => (
                    <div
                      key={item}
                      className="flex items-center gap-3 text-[12px] font-black uppercase tracking-[0.14em] text-slate-500"
                    >
                      <span className="h-2 w-2 rounded-full bg-primary/50" />
                      {item}
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-5 h-2.5 w-full overflow-hidden rounded-full bg-surface-container-highest/20">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: "67%" }}
                  transition={{ duration: 1.6, ease: "circOut" }}
                  className="h-full bg-gradient-to-r from-primary via-primary to-primary/10"
                />
              </div>
            </motion.div>
          </div>

          <motion.aside
            initial={{ opacity: 0, x: 18 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, delay: 0.18 }}
            className="flex min-h-[39rem] flex-col rounded-[2.25rem] border border-primary/10 bg-[rgba(46,53,69,0.45)] px-9 py-8 shadow-[0_10px_40px_rgba(0,0,0,0.35)] backdrop-blur-[40px]"
          >
            <h2 className="mb-6 font-headline text-[3.4rem] font-black leading-[0.95] tracking-tight text-white">
              Search Vault
            </h2>

            <div className="relative mb-10">
              <Search className="absolute left-5 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-500" />
              <input
                type="text"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Enter meal keywords..."
                className="w-full rounded-full bg-background/35 py-5 pl-14 pr-5 text-[1rem] font-medium text-white outline-none placeholder:text-slate-500"
              />
            </div>

            <div className="mb-3 text-[11px] font-black uppercase tracking-[0.3em] text-primary">
              Historical Stats
            </div>
            <div className="mb-3 border-b border-primary/10 pb-4 text-[1.15rem] font-black tracking-tight text-white">
              Recently Logged
            </div>

            <div className="space-y-0">
              {search.trim() && searchQuery.isLoading ? (
                <div className="rounded-2xl bg-background/20 p-5">
                  <LoadingState label="Searching foods..." className="text-primary" />
                </div>
              ) : search.trim() && searchQuery.isError ? (
                <ErrorState message={searchQuery.error.message} />
              ) : (
                vaultItems.map((item) => (
                  <SearchVaultRow
                    key={item.id}
                    item={item}
                    onAdd={item.food ? handleQuickAdd : undefined}
                  />
                ))
              )}
            </div>

            <div className="mt-auto pt-8">
              <div className="mb-5 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/15">
                    <Zap className="h-6 w-6 text-primary" />
                  </div>

                  <div>
                    <div className="text-[12px] font-black uppercase tracking-[0.28em] text-primary">
                      Chain Activation
                    </div>
                    <div className="mt-1 text-[2.3rem] font-black italic leading-none tracking-tight text-primary">
                      {chainActivationDays} Days
                    </div>
                  </div>
                </div>

                <Activity className="h-6 w-6 text-primary/70" />
              </div>

              <div className="h-2.5 w-full overflow-hidden rounded-full bg-surface-container-highest/20">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{
                    width: `${Math.min(Math.max(chainActivationDays * 10, 12), 100)}%`,
                  }}
                  transition={{ duration: 1.4, ease: "circOut" }}
                  className="h-full bg-primary"
                />
              </div>
            </div>
          </motion.aside>
        </section>

        <section className="mt-14 grid grid-cols-1 gap-12 md:grid-cols-2 xl:grid-cols-4">
          {metrics.map((metric) => (
            <motion.div
              key={metric.label}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: "easeOut" }}
            >
              <div className="text-[14px] font-black uppercase tracking-[0.34em] text-slate-500">
                {metric.label}
              </div>

              <div className="mt-6 flex items-end gap-3">
                <div className="font-headline text-[5.1rem] font-black leading-none tracking-tighter text-white">
                  {metric.value}
                </div>
                <div className="pb-3 text-[1.45rem] font-black uppercase tracking-[0.16em] text-slate-600">
                  {metric.unit}
                </div>
              </div>

              <div className="mt-8 h-2 w-full overflow-hidden rounded-full bg-surface-container-highest/20">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${metric.width}%` }}
                  transition={{ duration: 1.2, ease: "circOut" }}
                  className={cn("h-full", metric.barClass)}
                />
              </div>
            </motion.div>
          ))}
        </section>
      </main>

      <motion.div
        initial={{ opacity: 0, y: 20, x: 20 }}
        animate={{ opacity: 1, y: 0, x: 0 }}
        transition={{ duration: 0.5, delay: 0.35 }}
        className="fixed bottom-8 right-8 z-30 hidden min-w-[23rem] items-center gap-4 rounded-[1.65rem] border border-primary/10 bg-[rgba(46,53,69,0.5)] px-6 py-5 shadow-[0_10px_40px_rgba(0,0,0,0.35)] backdrop-blur-[40px] xl:flex"
      >
        <motion.div
          animate={{ y: [0, -4, 0] }}
          transition={{ duration: 2.8, repeat: Infinity, ease: "easeInOut" }}
          className="flex h-16 w-16 items-center justify-center rounded-full bg-primary"
        >
          <Bot className="h-8 w-8 text-on-primary" />
        </motion.div>

        <div>
          <div className="text-[12px] font-black uppercase tracking-[0.3em] text-primary">
            Neural Assistant
          </div>
          <div className="mt-1 text-[1.05rem] font-semibold text-slate-400">
            Listening for nutritional queries...
          </div>
        </div>
      </motion.div>

      <QuickLogModal
        food={selectedFood}
        open={Boolean(selectedFood)}
        onClose={() => setSelectedFood(null)}
        onConfirm={confirmQuickAdd}
        isPending={createMutation.isPending}
      />
    </div>
  );
}