"use client";

import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type ChangeEvent,
  type MouseEvent,
} from "react";
import { useRouter } from "next/navigation";
import {
  AnimatePresence,
  motion,
  useMotionValue,
  useSpring,
  useTransform,
} from "framer-motion";
import {
  AlertCircle,
  CheckCircle2,
  ChevronRight,
  ImagePlus,
  PencilLine,
  PlusCircle,
  Sparkles,
  UploadCloud,
  X,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { useAnalyzePhotoMutation } from "@/features/photo-estimator/hooks/use-analyze-photo-mutation";
import { useCreatePhotoFoodLogMutation } from "@/features/photo-estimator/hooks/use-create-photo-food-log-mutation";
import type {
  DetectedAnalysisItem,
  MealType,
} from "@/features/photo-estimator/types/photo-estimator.types";
import { cn } from "@/lib/utils/cn";

type ScreenMode = "idle" | "analyzing" | "results";

const fallbackImage =
  "https://images.unsplash.com/photo-1525351484163-7529414344d8?q=80&w=2000&auto=format&fit=crop";

const sampleItems: DetectedAnalysisItem[] = [
  {
    id: "sample-1",
    name: "Sourdough Bread",
    confidence: 98,
    amount: "2 slices",
    calories: 210,
    protein: 8,
    carbs: 38,
    fat: 2,
    weight: 80,
    unit: "g",
    position: { x: 50, y: 70 },
    foodItemId: null,
    per100Calories: 262,
    per100Protein: 10,
    per100Carbs: 47.5,
    per100Fat: 2.5,
  },
  {
    id: "sample-2",
    name: "Poached Egg",
    confidence: 95,
    amount: "2 large",
    calories: 144,
    protein: 13,
    carbs: 1,
    fat: 10,
    weight: 100,
    unit: "g",
    position: { x: 25, y: 25 },
    foodItemId: null,
    per100Calories: 144,
    per100Protein: 13,
    per100Carbs: 1,
    per100Fat: 10,
  },
  {
    id: "sample-3",
    name: "Avocado",
    confidence: 92,
    amount: "0.5 fruit",
    calories: 160,
    protein: 2,
    carbs: 9,
    fat: 15,
    weight: 100,
    unit: "g",
    position: { x: 65, y: 65 },
    foodItemId: null,
    per100Calories: 160,
    per100Protein: 2,
    per100Carbs: 9,
    per100Fat: 15,
  },
];

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
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

function scaleFromPer100(valuePer100: number, weight: number): number {
  return Math.round(valuePer100 * (weight / 100) * 10) / 10;
}

function recalcItem(item: DetectedAnalysisItem, weight: number): DetectedAnalysisItem {
  return {
    ...item,
    weight,
    amount: `${Math.round(weight)}g`,
    calories: Math.round(item.per100Calories * (weight / 100)),
    protein: scaleFromPer100(item.per100Protein, weight),
    carbs: scaleFromPer100(item.per100Carbs, weight),
    fat: scaleFromPer100(item.per100Fat, weight),
  };
}

function buildFallbackEditableItems(): DetectedAnalysisItem[] {
  return sampleItems.map((item, index) => ({
    ...item,
    id: `fallback-${index}-${item.id}`,
  }));
}

function EditLogMealModal({
  open,
  onClose,
  onConfirm,
  pending,
  hasMatchedItems,
}: Readonly<{
  open: boolean;
  onClose: () => void;
  onConfirm: (values: {
    loggedForDate: string;
    mealType: MealType;
    notes: string | null;
  }) => void;
  pending: boolean;
  hasMatchedItems: boolean;
}>) {
  const [loggedForDate, setLoggedForDate] = useState(todayIso());
  const [mealType, setMealType] = useState<MealType>("breakfast");
  const [notes, setNotes] = useState("");

  useEffect(() => {
    if (!open) {
      return;
    }

    setLoggedForDate(todayIso());
    setMealType("breakfast");
    setNotes("");
  }, [open]);

  if (!open) {
    return null;
  }

  return (
    <AnimatePresence>
      <motion.button
        key="log-meal-backdrop"
        type="button"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm"
      />

      <motion.div
        key="log-meal-panel"
        initial={{ opacity: 0, scale: 0.96, y: 18 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.98, y: 8 }}
        transition={{ duration: 0.2, ease: "easeOut" }}
        className="fixed inset-0 z-[110] flex items-center justify-center px-4"
      >
        <div className="w-full max-w-lg rounded-[1.75rem] border border-primary/10 bg-[rgba(20,27,43,0.82)] p-6 shadow-[0_20px_60px_rgba(0,0,0,0.45)] backdrop-blur-[40px]">
          <div className="mb-5">
            <div className="text-[10px] font-black uppercase tracking-[0.24em] text-primary">
              Log Meal
            </div>
            <h3 className="mt-2 font-headline text-3xl font-black tracking-tight text-white">
              Save analyzed meal
            </h3>
            <p className="mt-1 text-sm text-slate-400">
              Choose the date and meal type, then save the detected items to your log.
            </p>
          </div>

          {!hasMatchedItems ? (
            <div className="mb-5 rounded-xl bg-[#ffb4ab]/10 px-4 py-3 text-sm text-[#ffb4ab]">
              No detected item is mapped to your food catalog yet, so this meal cannot
              be logged automatically. Upload another photo or use manual food log.
            </div>
          ) : null}

          <div className="mb-5 rounded-xl bg-primary/10 px-4 py-3 text-sm text-primary">
            Manual edits on calories and macros are review-only for now. The saved food
            log still uses matched food catalog items plus grams until the backend gets
            override fields.
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
                Notes
              </span>
              <input
                type="text"
                value={notes}
                onChange={(event) => setNotes(event.target.value)}
                placeholder="Optional note..."
                className="w-full rounded-xl bg-surface-container-highest/30 px-4 py-3 text-sm font-semibold text-white outline-none placeholder:text-slate-500"
              />
            </label>
          </div>

          <div className="mb-5 flex flex-wrap gap-2">
            {(["breakfast", "lunch", "dinner", "snack"] as const).map((option) => (
              <button
                key={option}
                type="button"
                onClick={() => setMealType(option)}
                className={cn(
                  "rounded-full px-4 py-2 text-[10px] font-black uppercase tracking-widest transition-all",
                  mealType === option
                    ? "bg-primary text-on-primary"
                    : "bg-surface-container-highest/30 text-slate-400"
                )}
              >
                {option}
              </button>
            ))}
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
                  loggedForDate,
                  mealType,
                  notes: notes.trim() ? notes.trim() : null,
                })
              }
              disabled={pending || !hasMatchedItems}
              className="flex-1 rounded-xl bg-primary px-5 py-4 text-sm font-black text-on-primary shadow-[0_10px_30px_rgba(78,222,163,0.25)] disabled:opacity-70"
            >
              {pending ? "Saving..." : "Log This Meal"}
            </button>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}

export function PhotoEstimatorScreen({
  accessToken,
}: Readonly<{
  accessToken: string;
}>) {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const previewRef = useRef<string | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  const [previewUrl, setPreviewUrl] = useState<string>(fallbackImage);
  const [items, setItems] = useState<DetectedAnalysisItem[]>([]);
  const [screenMode, setScreenMode] = useState<ScreenMode>("idle");
  const [confirmed, setConfirmed] = useState(false);
  const [logModalOpen, setLogModalOpen] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [fallbackMode, setFallbackMode] = useState(false);

  const analyzeMutation = useAnalyzePhotoMutation();
  const createFoodLogMutation = useCreatePhotoFoodLogMutation();

  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const mouseXSpring = useSpring(x);
  const mouseYSpring = useSpring(y);

  const rotateX = useTransform(mouseYSpring, [-0.5, 0.5], ["7deg", "-7deg"]);
  const rotateY = useTransform(mouseXSpring, [-0.5, 0.5], ["-7deg", "7deg"]);

  useEffect(() => {
    return () => {
      if (previewRef.current) {
        URL.revokeObjectURL(previewRef.current);
      }
    };
  }, []);

  const handleMouseMove = (event: MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) {
      return;
    }

    const rect = containerRef.current.getBoundingClientRect();
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

  const totals = useMemo(() => {
    return items.reduce(
      (acc, item) => {
        acc.calories += item.calories;
        acc.protein += item.protein;
        acc.carbs += item.carbs;
        acc.fat += item.fat;
        return acc;
      },
      { calories: 0, protein: 0, carbs: 0, fat: 0 }
    );
  }, [items]);

  const hasMatchedItems = useMemo(
    () => items.some((item) => Boolean(item.foodItemId)),
    [items]
  );

  const triggerUploader = () => {
    fileInputRef.current?.click();
  };

  const handleFileSelected = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    if (previewRef.current) {
      URL.revokeObjectURL(previewRef.current);
    }

    const nextPreview = URL.createObjectURL(file);
    previewRef.current = nextPreview;
    setPreviewUrl(nextPreview);
    setAnalysisError(null);
    setConfirmed(false);
    setFallbackMode(false);
    setScreenMode("analyzing");
    setItems([]);

    analyzeMutation.mutate(
      {
        accessToken,
        file,
      },
      {
        onSuccess: (result) => {
          setItems(result.items);
          setScreenMode("results");
        },
        onError: (error) => {
          setAnalysisError(error.message);
          setItems(buildFallbackEditableItems());
          setFallbackMode(true);
          setScreenMode("results");
        },
      }
    );
  };

  const handleWeightChange = (itemId: string, weight: number) => {
    setItems((current) =>
      current.map((item) =>
        item.id === itemId ? recalcItem(item, weight) : item
      )
    );
  };

  const handleRemoveItem = (itemId: string) => {
    setItems((current) => current.filter((item) => item.id !== itemId));
  };

  const handleNameChange = (itemId: string, name: string) => {
    setItems((current) =>
      current.map((item) =>
        item.id === itemId
          ? {
              ...item,
              name,
            }
          : item
      )
    );
  };

  const handleMetricChange = (
    itemId: string,
    field: "calories" | "protein" | "carbs" | "fat",
    value: number
  ) => {
    setItems((current) =>
      current.map((item) => {
        if (item.id !== itemId) {
          return item;
        }

        const safeWeight = Math.max(item.weight, 1);
        const per100 = (value / safeWeight) * 100;

        if (field === "calories") {
          return {
            ...item,
            calories: Math.max(0, Math.round(value)),
            per100Calories: Math.max(0, per100),
          };
        }

        if (field === "protein") {
          return {
            ...item,
            protein: Math.max(0, Math.round(value * 10) / 10),
            per100Protein: Math.max(0, per100),
          };
        }

        if (field === "carbs") {
          return {
            ...item,
            carbs: Math.max(0, Math.round(value * 10) / 10),
            per100Carbs: Math.max(0, per100),
          };
        }

        return {
          ...item,
          fat: Math.max(0, Math.round(value * 10) / 10),
          per100Fat: Math.max(0, per100),
        };
      })
    );
  };

  const handleLogMeal = (values: {
    loggedForDate: string;
    mealType: MealType;
    notes: string | null;
  }) => {
    const loggableItems = items
      .filter((item) => Boolean(item.foodItemId))
      .map((item) => ({
        food_item_id: item.foodItemId as string,
        quantity: 1,
        grams: item.weight,
      }));

    createFoodLogMutation.mutate(
      {
        accessToken,
        payload: {
          logged_for_date: values.loggedForDate,
          meal_type: values.mealType,
          notes: values.notes,
          items: loggableItems,
        },
      },
      {
        onSuccess: () => {
          setConfirmed(true);
          setLogModalOpen(false);
        },
      }
    );
  };

  return (
    <div className="relative min-h-screen overflow-x-hidden bg-background text-foreground">
      <FloatingDecoration />

      <main className="relative z-10 mx-auto max-w-[1600px] px-4 py-4 sm:px-6 lg:px-12 lg:py-8">
        <div className="flex flex-col gap-8 lg:flex-row perspective-[1000px]">
          <motion.section
            className="space-y-6 lg:w-3/5"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8 }}
          >
            <div className="flex items-center justify-between">
              <h1 className="font-headline text-3xl font-extrabold tracking-tight">
                Analysis Results
              </h1>

              <div className="flex items-center gap-2 rounded-full border border-primary/15 bg-primary/10 px-4 py-1.5 text-primary">
                <Sparkles className="h-3.5 w-3.5 fill-primary" />
                <span className="text-[10px] font-black uppercase tracking-widest">
                  AI Enhanced
                </span>
              </div>
            </div>

            {analysisError ? <ErrorState message={analysisError} /> : null}

            {fallbackMode ? (
              <div className="rounded-xl bg-primary/10 px-4 py-3 text-sm text-primary">
                Vision model fallback is active right now. You can still review and edit
                the estimates on this screen while the real vision model is pending.
              </div>
            ) : null}

            <motion.div
              ref={containerRef}
              onMouseMove={handleMouseMove}
              onMouseLeave={handleMouseLeave}
              style={{
                rotateX,
                rotateY,
                transformStyle: "preserve-3d",
              }}
              className="group relative overflow-hidden rounded-2xl border border-white/5 bg-muted shadow-[0_50px_100px_-20px_rgba(0,0,0,0.5)]"
            >
              <motion.img
                src={previewUrl}
                alt="Analyzed meal"
                className={cn(
                  "h-[500px] w-full object-cover transition-transform duration-700 lg:h-[716px]",
                  screenMode === "idle" ? "scale-[1.08] blur-[1px]" : ""
                )}
                referrerPolicy="no-referrer"
                style={{ transform: "translateZ(-20px) scale(1.1)" }}
              />

              <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(78,222,163,0.12),transparent_70%)]" />

              {screenMode !== "idle" ? (
                <div className="pointer-events-none absolute inset-0 h-40 w-full animate-scan bg-gradient-to-b from-transparent via-primary/20 to-transparent mix-blend-screen" />
              ) : null}

              {screenMode === "idle" ? (
                <div className="absolute inset-0 z-20 flex items-center justify-center bg-black/30 backdrop-blur-[2px]">
                  <div className="mx-6 max-w-md rounded-[2rem] border border-primary/15 bg-[rgba(20,27,43,0.72)] p-8 text-center shadow-[0_20px_60px_rgba(0,0,0,0.45)] backdrop-blur-[30px]">
                    <div className="mx-auto mb-5 flex h-20 w-20 items-center justify-center rounded-full bg-primary/10 text-primary">
                      <UploadCloud className="h-10 w-10" />
                    </div>

                    <h2 className="font-headline text-3xl font-black tracking-tight text-white">
                      Upload a photo to analyze
                    </h2>

                    <p className="mt-3 text-sm leading-relaxed text-slate-400">
                      Start with an image first. Then this page will scan it, estimate
                      food types and macros, and let you edit the results before logging.
                    </p>

                    <button
                      type="button"
                      onClick={triggerUploader}
                      className="mt-6 rounded-full bg-primary px-8 py-4 text-[10px] font-black uppercase tracking-[0.24em] text-on-primary shadow-[0_10px_30px_rgba(78,222,163,0.25)] transition-all hover:scale-[1.02]"
                    >
                      Add Photo To Analyze
                    </button>
                  </div>
                </div>
              ) : null}

              {screenMode === "analyzing" ? (
                <div className="absolute inset-0 z-20 flex items-center justify-center bg-black/35 backdrop-blur-sm">
                  <LoadingState
                    label="Running vision inference..."
                    className="text-primary"
                  />
                </div>
              ) : null}

              {screenMode === "results" ? (
                <>
                  <div
                    className="absolute right-4 top-4 z-20 cursor-pointer rounded-full border border-primary/20 bg-background/40 px-4 py-2 text-[10px] font-black uppercase tracking-[0.22em] text-primary opacity-0 backdrop-blur-xl transition-opacity group-hover:opacity-100"
                    onClick={triggerUploader}
                  >
                    Analyze another photo
                  </div>

                  {items.map((item) => (
                    <motion.div
                      key={item.id}
                      className="absolute"
                      style={{
                        left: `${item.position.x}%`,
                        top: `${item.position.y}%`,
                        transform: "translateZ(50px)",
                        transformStyle: "preserve-3d",
                      }}
                      initial={{ scale: 0, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ delay: 0.45 }}
                    >
                      <div className="-translate-x-1/2 -translate-y-1/2 flex flex-col items-center">
                        <div className="h-4 w-4 animate-pulse rounded-full bg-primary shadow-[0_0_20px_rgba(78,222,163,0.9)]" />
                        <motion.div
                          initial={{ y: 5 }}
                          animate={{ y: 0 }}
                          className="mt-3 whitespace-nowrap rounded-lg border border-primary/40 bg-[rgba(20,27,43,0.6)] px-3 py-1.5 shadow-xl backdrop-blur-[24px]"
                          style={{ transform: "translateZ(80px)" }}
                        >
                          <span className="flex items-center gap-2 text-[10px] font-bold leading-none tracking-tight text-white">
                            <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                            {item.name} ({item.confidence}%)
                          </span>
                        </motion.div>
                      </div>
                    </motion.div>
                  ))}
                </>
              ) : null}

              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={handleFileSelected}
              />
            </motion.div>
          </motion.section>

          <motion.section
            className="lg:w-2/5"
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <Card className="group relative flex h-full flex-col overflow-hidden border-border/10 bg-[rgba(20,27,43,0.6)] p-6 shadow-2xl backdrop-blur-[24px] lg:p-8">
              <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-white/5 to-transparent" />

              <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
                {[
                  {
                    label: "Calories",
                    value: totals.calories || 0,
                    color: "text-foreground",
                    border: "",
                  },
                  {
                    label: "Protein",
                    value: `${Math.round(totals.protein || 0)}g`,
                    color: "text-primary",
                    border: "border-primary",
                  },
                  {
                    label: "Carbs",
                    value: `${Math.round(totals.carbs || 0)}g`,
                    color: "text-secondary",
                    border: "border-secondary",
                  },
                  {
                    label: "Fats",
                    value: `${Math.round(totals.fat || 0)}g`,
                    color: "text-tertiary",
                    border: "border-tertiary",
                  },
                ].map((stat, index) => (
                  <motion.div
                    key={stat.label}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.35 + index * 0.08 }}
                    className={`rounded-2xl border-b-4 bg-background/40 p-4 text-center shadow-lg backdrop-blur-md ${stat.border}`}
                  >
                    <div
                      className={`mb-1 font-headline text-xl font-bold leading-none lg:text-2xl ${stat.color}`}
                    >
                      {stat.value}
                    </div>
                    <div className="text-[9px] font-black uppercase tracking-widest text-muted-foreground">
                      {stat.label}
                    </div>
                  </motion.div>
                ))}
              </div>

              <div className="mb-6 flex items-center justify-between">
                <h2 className="font-headline text-lg font-bold">Detected Items</h2>

                <button
                  type="button"
                  onClick={() => router.push("/food-log")}
                  className="flex items-center gap-1.5 text-xs font-black uppercase tracking-widest text-primary transition-all hover:scale-105 hover:opacity-80"
                >
                  <PlusCircle className="h-4 w-4" />
                  Manual Log
                </button>
              </div>

              <div className="max-h-[400px] flex-grow space-y-4 overflow-y-auto pr-2 lg:max-h-[500px]">
                {screenMode === "idle" ? (
                  <div className="rounded-2xl border border-white/5 bg-accent/20 p-6 text-sm text-slate-400">
                    Upload a photo first. After analysis, detected foods will appear here
                    with editable weight, calories, protein, carbs, and fat.
                  </div>
                ) : screenMode === "analyzing" ? (
                  <div className="rounded-2xl border border-white/5 bg-accent/20 p-6">
                    <LoadingState
                      label="Extracting detected foods..."
                      className="text-primary"
                    />
                  </div>
                ) : (
                  <AnimatePresence mode="popLayout">
                    {items.map((item, index) => (
                      <motion.div
                        key={item.id}
                        layout
                        initial={{ opacity: 0, y: 20, rotateX: -10 }}
                        animate={{ opacity: 1, y: 0, rotateX: 0 }}
                        exit={{ opacity: 0, scale: 0.9, rotateX: 10 }}
                        transition={{ delay: index * 0.05 }}
                        className="group cursor-default rounded-2xl border border-white/5 bg-accent/30 p-5 shadow-sm transition-all hover:bg-accent/50 hover:shadow-md"
                      >
                        <div className="mb-3 flex items-start justify-between gap-3">
                          <div className="min-w-0 flex-1">
                            <div className="mb-2 flex items-center gap-2">
                              <PencilLine className="h-3.5 w-3.5 text-primary" />
                              <span className="text-[9px] font-black uppercase tracking-widest text-primary">
                                Editable
                              </span>
                            </div>

                            <input
                              type="text"
                              value={item.name}
                              onChange={(event) =>
                                handleNameChange(item.id, event.target.value)
                              }
                              className="w-full bg-transparent text-sm font-bold outline-none"
                            />

                            <div className="mt-2 flex flex-wrap items-center gap-2">
                              <div className="h-4 rounded border border-primary/20 bg-primary/10 px-1.5 text-[8px] font-black uppercase text-primary">
                                {item.confidence}% Confidence
                              </div>

                              <span className="text-[10px] font-medium text-muted-foreground">
                                {item.amount} ({Math.round(item.weight)}
                                {item.unit})
                              </span>

                              {item.foodItemId ? (
                                <span className="text-[8px] font-black uppercase tracking-widest text-primary">
                                  Catalog matched
                                </span>
                              ) : (
                                <span className="flex items-center gap-1 text-[8px] font-black uppercase tracking-widest text-[#ffb4ab]">
                                  <AlertCircle className="h-3 w-3" />
                                  No catalog match
                                </span>
                              )}
                            </div>
                          </div>

                          <button
                            type="button"
                            onClick={() => handleRemoveItem(item.id)}
                            className="p-1 text-muted-foreground transition-colors hover:text-destructive"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </div>

                        <div className="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
                          {[
                            {
                              label: "Calories",
                              value: item.calories,
                              color: "text-muted-foreground",
                              onChange: (next: number) =>
                                handleMetricChange(item.id, "calories", next),
                            },
                            {
                              label: "Protein",
                              value: item.protein,
                              color: "text-primary",
                              onChange: (next: number) =>
                                handleMetricChange(item.id, "protein", next),
                            },
                            {
                              label: "Carbs",
                              value: item.carbs,
                              color: "text-secondary",
                              onChange: (next: number) =>
                                handleMetricChange(item.id, "carbs", next),
                            },
                            {
                              label: "Fat",
                              value: item.fat,
                              color: "text-tertiary",
                              onChange: (next: number) =>
                                handleMetricChange(item.id, "fat", next),
                            },
                          ].map((metric) => (
                            <div key={metric.label}>
                              <div
                                className={`mb-1 text-[8px] font-black uppercase tracking-widest ${metric.color}`}
                              >
                                {metric.label}
                              </div>
                              <input
                                type="number"
                                min="0"
                                step="0.1"
                                value={metric.value}
                                onChange={(event) =>
                                  metric.onChange(
                                    Math.max(0, Number(event.target.value) || 0)
                                  )
                                }
                                className="w-full rounded-lg bg-background/40 px-3 py-2 text-sm font-bold outline-none"
                              />
                            </div>
                          ))}
                        </div>

                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-[10px] font-black uppercase tracking-widest text-muted-foreground">
                            <span>Weight</span>
                            <span>
                              {Math.round(item.weight)}
                              {item.unit}
                            </span>
                          </div>

                          <Slider
                            value={[item.weight]}
                            onValueChange={(value) =>
                              handleWeightChange(item.id, value[0] ?? item.weight)
                            }
                            min={20}
                            max={400}
                            step={5}
                            className="py-2"
                          />
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                )}
              </div>

              <div className="mt-6 border-t border-border/10 pt-6">
                {createFoodLogMutation.isError ? (
                  <div className="mb-4 rounded-xl bg-[#ffb4ab]/10 px-4 py-3 text-sm text-[#ffb4ab]">
                    {createFoodLogMutation.error.message}
                  </div>
                ) : null}

                {confirmed ? (
                  <div className="mb-4 flex items-center gap-2 rounded-xl bg-primary/10 px-4 py-3 text-sm text-primary">
                    <CheckCircle2 className="h-4 w-4" />
                    Meal logged successfully.
                  </div>
                ) : null}

                <div className="mb-4 rounded-xl bg-primary/10 px-4 py-3 text-sm text-primary">
                  You can edit estimated calories and macros here before saving. Those
                  edits are reflected in the UI review step immediately.
                </div>

                <div className="flex flex-col gap-4 sm:flex-row">
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() => setConfirmed(true)}
                    disabled={screenMode !== "results"}
                    className="order-2 h-14 flex-1 rounded-full border border-white/5 font-black uppercase tracking-widest text-[10px] hover:bg-accent sm:order-1"
                  >
                    Confirm All
                  </Button>

                  <Button
                    type="button"
                    onClick={() => setLogModalOpen(true)}
                    disabled={screenMode !== "results" || items.length === 0}
                    className="order-1 h-14 flex-[2] rounded-full bg-primary text-primary-foreground shadow-[0_8px_25px_-4px_rgba(78,222,163,0.3)] transition-all hover:scale-[1.02] sm:order-2"
                  >
                    <span className="text-[10px] font-black uppercase tracking-widest">
                      Log This Meal
                    </span>
                    <ChevronRight className="ml-1 h-4 w-4" />
                  </Button>
                </div>
              </div>
            </Card>
          </motion.section>
        </div>
      </main>

      <EditLogMealModal
        open={logModalOpen}
        onClose={() => setLogModalOpen(false)}
        onConfirm={handleLogMeal}
        pending={createFoodLogMutation.isPending}
        hasMatchedItems={hasMatchedItems}
      />

      <style jsx global>{`
        @keyframes scan {
          0% {
            transform: translateY(-100%);
          }
          100% {
            transform: translateY(716px);
          }
        }

        .animate-scan {
          animation: scan 3s linear infinite;
        }
      `}</style>
    </div>
  );
}