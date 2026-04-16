"use client";

import { useEffect, useMemo, useRef } from "react";
import { useRouter } from "next/navigation";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  AnimatePresence,
  motion,
  useMotionValue,
  useSpring,
  useTransform,
  type Variants,
} from "framer-motion";
import {
  Activity,
  CheckCircle2,
  Dumbbell,
  Flame,
  Search,
  Scale,
  TrendingDown,
  User,
  UserCircle,
  X,
  Zap,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { useProfileQuery } from "@/features/onboarding/hooks/use-profile-query";
import { useCurrentGoalQuery } from "@/features/onboarding/hooks/use-current-goal-query";
import { useSaveGoalSetupMutation } from "@/features/onboarding/hooks/use-save-goal-setup-mutation";
import {
  goalsSchema,
  type GoalsFormValues,
} from "@/features/onboarding/schemas/goals.schema";
import { mapObjectiveToGoalType } from "@/features/onboarding/api/goals";
import { cn } from "@/lib/utils/cn";

const DIET_OPTIONS = [
  "Vegetarian",
  "Keto",
  "Paleo",
  "Vegan",
  "Halal",
  "Pescatarian",
  "Low Carb",
] as const;

const CUSTOM_EASING = [0.16, 1, 0.3, 1] as const;

const sectionVariants: Variants = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.7,
      ease: CUSTOM_EASING,
    },
  },
};

type ObjectiveId = "lose" | "maintain" | "gain";

function MagneticWrapper({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const ref = useRef<HTMLDivElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const springX = useSpring(x, { stiffness: 150, damping: 15 });
  const springY = useSpring(y, { stiffness: 150, damping: 15 });

  const handleMouseMove = (event: React.MouseEvent) => {
    if (!ref.current) {
      return;
    }

    const { clientX, clientY } = event;
    const { left, top, width, height } = ref.current.getBoundingClientRect();
    const centerX = left + width / 2;
    const centerY = top + height / 2;

    x.set((clientX - centerX) * 0.35);
    y.set((clientY - centerY) * 0.35);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{ x: springX, y: springY }}
    >
      {children}
    </motion.div>
  );
}

function TiltCard({
  children,
  className,
}: Readonly<{
  children: React.ReactNode;
  className?: string;
}>) {
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const mouseXSpring = useSpring(x);
  const mouseYSpring = useSpring(y);

  const rotateX = useTransform(mouseYSpring, [-0.5, 0.5], ["15deg", "-15deg"]);
  const rotateY = useTransform(mouseXSpring, [-0.5, 0.5], ["-15deg", "15deg"]);

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
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        rotateY,
        rotateX,
        transformStyle: "preserve-3d",
      }}
      className={cn("relative", className)}
    >
      {children}
    </motion.div>
  );
}

function ObjectiveCard({
  selected,
  onClick,
  icon,
  title,
  description,
}: Readonly<{
  selected: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  title: string;
  description: string;
}>) {
  return (
    <motion.button
      type="button"
      whileHover={{ y: -8, scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={cn(
        "relative flex h-full flex-col overflow-hidden rounded-[2rem] border p-8 text-left transition-all duration-500",
        selected
          ? "border-primary bg-primary/10 ring-1 ring-primary/50 shadow-[0_0_30px_rgba(78,222,163,0.15)]"
          : "border-transparent bg-[linear-gradient(135deg,rgba(16,185,129,0.1)_0%,rgba(20,27,43,0.4)_100%)] backdrop-blur-[24px] hover:border-primary/30 hover:bg-white/5"
      )}
    >
      {selected ? (
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="absolute right-6 top-6 text-primary"
        >
          <CheckCircle2 className="h-6 w-6 fill-primary text-on-primary" />
        </motion.div>
      ) : null}

      <div
        className={cn(
          "mb-6 flex h-14 w-14 items-center justify-center rounded-2xl transition-all duration-500",
          selected ? "scale-110 bg-primary text-on-primary" : "bg-surface-container-low text-primary"
        )}
      >
        {icon}
      </div>

      <h3 className="mb-2 text-xl font-bold text-on-surface">{title}</h3>
      <p className={cn("text-sm leading-relaxed", selected ? "text-on-surface/80" : "text-on-surface-variant")}>
        {description}
      </p>
    </motion.button>
  );
}

function KineticBackground() {
  return (
    <>
      <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
        <div className="absolute left-[-10%] top-[-10%] h-[40%] w-[40%] rounded-full bg-primary/10 blur-[120px]" />
        <div className="absolute bottom-[10%] right-[-5%] h-[35%] w-[35%] rounded-full bg-secondary/5 blur-[100px]" />
        <div className="absolute right-[15%] top-[20%] h-[25%] w-[25%] rounded-full bg-primary/5 blur-[80px]" />
      </div>
      <div
        className="pointer-events-none fixed inset-0 z-0 opacity-[0.03]"
        style={{
          backgroundImage: "radial-gradient(#4edea3 0.6px, transparent 0.6px)",
          backgroundSize: "24px 24px",
        }}
      />
    </>
  );
}

export function GoalsForm({
  accessToken,
}: Readonly<{
  accessToken: string;
}>) {
  const router = useRouter();
  const profileQuery = useProfileQuery(accessToken);
  const currentGoalQuery = useCurrentGoalQuery(accessToken);
  const saveGoalSetupMutation = useSaveGoalSetupMutation();

  const {
    control,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<GoalsFormValues>({
    resolver: zodResolver(goalsSchema),
    defaultValues: {
      objective: "maintain",
      weeklyChange: 0,
      dietaryFocus: [],
      exclusions: [],
    },
  });

  const objective = watch("objective") ?? "maintain";
  const weeklyChange = watch("weeklyChange") ?? 0;
  const dietaryFocus = watch("dietaryFocus") ?? [];
  const exclusions = watch("exclusions") ?? [];

  useEffect(() => {
    if (profileQuery.data === null) {
      router.replace("/personal-details");
    }
  }, [profileQuery.data, router]);

  useEffect(() => {
    if (!currentGoalQuery.data) {
      return;
    }

    const currentGoal = currentGoalQuery.data;
    const mappedObjective: ObjectiveId =
      currentGoal.goal_type === "weight_loss"
        ? "lose"
        : currentGoal.goal_type === "muscle_gain" || currentGoal.goal_type === "weight_gain"
        ? "gain"
        : "maintain";

    setValue("objective", mappedObjective);
    setValue("weeklyChange", currentGoal.weekly_target_rate_kg ?? 0);
  }, [currentGoalQuery.data, setValue]);

  useEffect(() => {
    if (!profileQuery.data) {
      return;
    }

    const nextDietaryFocus = profileQuery.data.dietary_preferences
      .filter((item) => item.preference_type === "diet_type")
      .map((item) => item.value);

    const nextExclusions = profileQuery.data.dietary_preferences
      .filter((item) => item.preference_type === "restriction")
      .map((item) => item.value);

    setValue("dietaryFocus", nextDietaryFocus);
    setValue("exclusions", nextExclusions);
  }, [profileQuery.data, setValue]);

  const goalSummary = useMemo(() => {
    if (!profileQuery.data) {
      return {
        dailyTarget: "—",
        tdee: "—",
        bmr: "—",
      };
    }

    const weight = profileQuery.data.current_weight_kg ?? 0;
    const height = profileQuery.data.height_cm ?? 0;
    const age = profileQuery.data.age ?? 25;
    const sex = profileQuery.data.sex === "female" ? "female" : "male";
    const activityLevel =
      profileQuery.data.activity_profile?.activity_level ?? "moderately_active";

    const baseBmr =
      sex === "male"
        ? 10 * weight + 6.25 * height - 5 * age + 5
        : 10 * weight + 6.25 * height - 5 * age - 161;

    const multiplierMap: Record<string, number> = {
      sedentary: 1.2,
      lightly_active: 1.375,
      moderately_active: 1.55,
      very_active: 1.725,
      extra_active: 1.9,
    };

    const estimatedTdee = baseBmr * (multiplierMap[activityLevel] ?? 1.55);

    let dailyTarget = estimatedTdee;
    if (objective === "lose") {
      dailyTarget = estimatedTdee - weeklyChange * 1100;
    } else if (objective === "gain") {
      dailyTarget = estimatedTdee + weeklyChange * 900;
    }

    return {
      dailyTarget: Math.round(dailyTarget).toLocaleString(),
      tdee: Math.round(estimatedTdee).toLocaleString(),
      bmr: Math.round(baseBmr).toLocaleString(),
    };
  }, [objective, profileQuery.data, weeklyChange]);

  const toggleDiet = (diet: string) => {
    const current = dietaryFocus;
    if (current.includes(diet)) {
      setValue(
        "dietaryFocus",
        current.filter((item) => item !== diet),
        { shouldValidate: true }
      );
    } else {
      setValue("dietaryFocus", [...current, diet], { shouldValidate: true });
    }
  };

  const removeExclusion = (item: string) => {
    setValue(
      "exclusions",
      exclusions.filter((entry) => entry !== item),
      { shouldValidate: true }
    );
  };

  const handleObjectiveChange = (value: ObjectiveId) => {
    setValue("objective", value, { shouldValidate: true });

    if (value === "maintain") {
      setValue("weeklyChange", 0, { shouldValidate: true });
    } else if (weeklyChange === 0) {
      setValue("weeklyChange", 0.4, { shouldValidate: true });
    }
  };

  const onSubmit = (data: GoalsFormValues) => {
    saveGoalSetupMutation.mutate(
      {
        accessToken,
        payload: {
          goal: {
            goal_type: mapObjectiveToGoalType(data.objective),
            calculation_mode: "calculated",
            bmr_formula: "mifflin_st_jeor",
            weekly_target_rate_kg:
              data.objective === "maintain" ? null : data.weeklyChange,
            target_weight_kg: null,
            notes: null,
          },
          dietaryFocus: data.dietaryFocus,
          exclusions: data.exclusions,
        },
      },
      {
        onSuccess: () => {
          router.push("/plan");
        },
      }
    );
  };

  if (profileQuery.isLoading || currentGoalQuery.isLoading) {
    return (
      <div className="w-full max-w-5xl rounded-[2rem] bg-surface-container-low/40 p-10 backdrop-blur-2xl">
        <LoadingState label="Preparing your goal setup..." className="text-primary" />
      </div>
    );
  }

  if (profileQuery.isError) {
    return (
      <div className="w-full max-w-5xl rounded-[2rem] bg-surface-container-low/40 p-10 backdrop-blur-2xl">
        <ErrorState message={profileQuery.error.message} />
      </div>
    );
  }

  if (currentGoalQuery.isError) {
    return (
      <div className="w-full max-w-5xl rounded-[2rem] bg-surface-container-low/40 p-10 backdrop-blur-2xl">
        <ErrorState message={currentGoalQuery.error.message} />
      </div>
    );
  }

  if (!profileQuery.data) {
    return null;
  }

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-background text-on-surface">
      <KineticBackground />

      <div className="relative z-10 mx-auto w-full max-w-6xl py-10">
        <header className="mb-12 flex flex-col items-start gap-12 md:flex-row">
          <div className="flex-1">
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, ease: CUSTOM_EASING }}
              className="mb-6 font-headline text-4xl font-extrabold leading-[1.1] tracking-tight md:text-6xl"
            >
              Set Your{" "}
              <span className="relative text-primary">
                Performance Target
                <motion.span
                  animate={{ opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 3, repeat: Infinity }}
                  className="absolute -inset-1 -z-10 rounded-full bg-primary/10 blur-xl"
                />
              </span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, delay: 0.2, ease: CUSTOM_EASING }}
              className="max-w-xl text-xl leading-relaxed text-on-surface-variant"
            >
              Refine your physical goals and nutritional boundaries to help our AI
              craft your <span className="font-medium text-on-surface">optimal metabolic fuel plan</span>.
            </motion.p>
          </div>

          <TiltCard className="w-full shrink-0 md:w-[400px]">
            <div className="relative flex h-[280px] flex-col justify-between overflow-hidden rounded-[2.5rem] border border-white/5 p-8 shadow-2xl">
              <div className="absolute inset-0 -z-20 bg-[#0A0A0A]" />
              <div className="absolute -right-24 -top-24 z-0 h-48 w-48 rounded-full bg-primary/10 blur-[100px]" />
              <div className="absolute -bottom-24 -left-24 z-0 h-48 w-48 rounded-full bg-secondary/10 blur-[100px]" />

              <motion.div
                style={{ translateZ: 60 }}
                className="absolute right-8 top-8 z-20 w-40 rounded-3xl border border-white/10 bg-white/[0.03] p-5 shadow-2xl backdrop-blur-2xl"
              >
                <div className="mb-3 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Activity className="h-3.5 w-3.5 text-primary" />
                    <span className="text-[9px] font-bold uppercase tracking-[0.2em] text-white/50">
                      Metabolism
                    </span>
                  </div>
                  <span className="text-[10px] font-black text-primary">75%</span>
                </div>

                <div className="relative h-1 w-full overflow-hidden rounded-full bg-white/5">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: "75%" }}
                    transition={{ duration: 2, ease: CUSTOM_EASING }}
                    className="absolute inset-y-0 left-0 bg-primary"
                  />
                  <motion.div
                    animate={{ x: ["-100%", "200%"] }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    className="absolute inset-y-0 w-1/2 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                  />
                </div>
              </motion.div>

              <motion.div
                style={{ translateZ: 100 }}
                className="absolute bottom-8 left-8 z-30 flex items-center gap-3 rounded-2xl bg-white px-5 py-2.5 text-xs font-bold text-black shadow-2xl"
              >
                <div className="relative">
                  <Zap className="h-3.5 w-3.5 fill-current" />
                  <motion.div
                    animate={{ scale: [1, 2], opacity: [0.3, 0] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="absolute inset-0 -z-10 rounded-full bg-black"
                  />
                </div>
                Peak Energy
              </motion.div>

              <div className="absolute inset-0 -z-10 overflow-hidden">
                <motion.img
                  src="https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&q=80&w=1000"
                  alt="Athlete Training"
                  referrerPolicy="no-referrer"
                  animate={{
                    scale: [1, 1.05, 1],
                    opacity: [0.6, 0.8, 0.6],
                  }}
                  transition={{
                    duration: 10,
                    repeat: Infinity,
                    ease: "easeInOut",
                  }}
                  className="h-full w-full object-cover brightness-75 contrast-125 grayscale"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#0A0A0A] via-transparent to-[#0A0A0A]/40" />
                <div
                  className="absolute inset-0 opacity-30"
                  style={{
                    backgroundImage:
                      "radial-gradient(circle, #4EDEA3 1px, transparent 1px)",
                    backgroundSize: "24px 24px",
                  }}
                />
              </div>

              <div className="relative z-10 mt-auto">
                <div className="text-[10px] font-bold uppercase tracking-[0.3em] text-white/50">
                  AI Engine v2.4
                </div>
              </div>
            </div>
          </TiltCard>
        </header>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-16 pb-20">
          <motion.section
            variants={sectionVariants}
            initial="hidden"
            animate="visible"
            className="space-y-8"
          >
            <h2 className="flex items-center gap-4 text-2xl font-bold">
              <span className="h-8 w-2 rounded-full bg-primary" />
              Primary Fitness Objective
            </h2>

            <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
              {[
                {
                  id: "lose" as const,
                  icon: <TrendingDown className="h-8 w-8" />,
                  title: "Lose Weight",
                  desc: "Prioritize fat loss and metabolic efficiency.",
                },
                {
                  id: "maintain" as const,
                  icon: <Scale className="h-8 w-8" />,
                  title: "Maintain",
                  desc: "Keep current weight and improve body composition.",
                },
                {
                  id: "gain" as const,
                  icon: <Dumbbell className="h-8 w-8" />,
                  title: "Gain Muscle",
                  desc: "Focus on muscle hypertrophy and strength.",
                },
              ].map((item) => (
                <ObjectiveCard
                  key={item.id}
                  selected={objective === item.id}
                  onClick={() => handleObjectiveChange(item.id)}
                  icon={item.icon}
                  title={item.title}
                  description={item.desc}
                />
              ))}
            </div>
          </motion.section>

          <AnimatePresence mode="wait">
            {objective !== "maintain" ? (
              <motion.section
                key="weekly-change"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.6, ease: CUSTOM_EASING }}
                className="space-y-10 overflow-hidden rounded-[2rem] bg-[linear-gradient(135deg,rgba(16,185,129,0.1)_0%,rgba(20,27,43,0.4)_100%)] p-10 backdrop-blur-[24px]"
              >
                <div className="flex items-end justify-between">
                  <div className="space-y-2">
                    <h2 className="text-2xl font-bold">Target Weekly Change</h2>
                    <p className="text-base text-on-surface-variant">
                      Recommended: 0.2kg - 0.5kg for sustainable results.
                    </p>
                  </div>

                  <div className="font-headline text-4xl font-black text-primary">
                    {weeklyChange.toFixed(1)}{" "}
                    <span className="text-lg font-normal text-on-surface-variant">
                      kg/week
                    </span>
                  </div>
                </div>

                <div className="px-2 py-8">
                  <Controller
                    name="weeklyChange"
                    control={control}
                    render={({ field }) => (
                      <div className="group relative">
                        <Slider
                          value={[field.value]}
                          onValueChange={(values) => {
                            if (values.length > 0) {
                              field.onChange(values[0]);
                            }
                          }}
                          min={0.1}
                          max={1}
                          step={0.1}
                          className="cursor-pointer py-6"
                        />
                        <div className="pointer-events-none absolute inset-x-0 top-1/2 -z-10 h-2 -translate-y-1/2 rounded-full bg-white/5" />
                      </div>
                    )}
                  />

                  <div className="mt-6 flex justify-between text-[10px] font-bold uppercase tracking-[0.2em] text-on-surface-variant">
                    <span className={cn(weeklyChange <= 0.3 && "text-primary")}>
                      Conservative
                    </span>
                    <span
                      className={cn(
                        weeklyChange > 0.3 &&
                          weeklyChange <= 0.7 &&
                          "text-primary"
                      )}
                    >
                      Moderate
                    </span>
                    <span className={cn(weeklyChange > 0.7 && "text-primary")}>
                      Aggressive
                    </span>
                  </div>
                </div>
              </motion.section>
            ) : null}
          </AnimatePresence>

          <div className="grid grid-cols-1 gap-10 md:grid-cols-[1.2fr_0.8fr]">
            <motion.section
              variants={sectionVariants}
              initial="hidden"
              animate="visible"
              className="space-y-8"
            >
              <h2 className="flex items-center gap-4 text-2xl font-bold">
                <span className="h-8 w-2 rounded-full bg-secondary" />
                Dietary Focus
              </h2>

              <div className="flex flex-wrap gap-3">
                {DIET_OPTIONS.map((diet) => (
                  <motion.button
                    key={diet}
                    type="button"
                    whileHover={{ scale: 1.04 }}
                    whileTap={{ scale: 0.96 }}
                    onClick={() => toggleDiet(diet)}
                    className={cn(
                      "rounded-full border px-6 py-3 text-sm font-bold transition-all",
                      dietaryFocus.includes(diet)
                        ? "border-primary/20 bg-primary/10 text-primary hover:bg-primary/20"
                        : "border-transparent bg-surface-container-low text-on-surface-variant hover:bg-surface-container-high"
                    )}
                  >
                    {diet}
                  </motion.button>
                ))}
              </div>

              <p className="text-sm text-[#ffb4ab]">
                {errors.dietaryFocus?.message}
              </p>
            </motion.section>

            <motion.section
              variants={sectionVariants}
              initial="hidden"
              animate="visible"
              className="space-y-8"
            >
              <h2 className="flex items-center gap-4 text-2xl font-bold">
                <span className="h-8 w-2 rounded-full bg-[#ffb4ab]" />
                Exclusions
              </h2>

              <div className="relative">
                <Search className="absolute left-5 top-1/2 h-5 w-5 -translate-y-1/2 text-on-surface-variant" />
                <Input
                  className="h-14 rounded-2xl border-none bg-surface-container-low/70 pl-14 text-lg focus-visible:ring-2 focus-visible:ring-primary"
                  placeholder="Search allergies or foods..."
                  onKeyDown={(event) => {
                    if (event.key !== "Enter") {
                      return;
                    }

                    event.preventDefault();
                    const value = event.currentTarget.value.trim();

                    if (value && !exclusions.includes(value)) {
                      setValue("exclusions", [...exclusions, value], {
                        shouldValidate: true,
                      });
                    }

                    event.currentTarget.value = "";
                  }}
                />
              </div>

              <div className="flex min-h-[44px] flex-wrap gap-3">
                {exclusions.map((item) => (
                  <motion.div
                    key={item}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="inline-flex items-center gap-2 rounded-full border border-[#ffb4ab]/20 bg-[#ffb4ab]/10 px-4 py-2 text-sm font-medium text-[#ffb4ab]"
                  >
                    {item}
                    <button
                      type="button"
                      onClick={() => removeExclusion(item)}
                      className="transition-opacity hover:opacity-80"
                      aria-label={`Remove ${item}`}
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </motion.div>
                ))}
              </div>

              <p className="text-sm text-[#ffb4ab]">
                {errors.exclusions?.message}
              </p>
            </motion.section>
          </div>

          {saveGoalSetupMutation.isError ? (
            <div className="rounded-2xl bg-[#ffb4ab]/10 px-4 py-3 text-sm text-[#ffb4ab]">
              {saveGoalSetupMutation.error.message}
            </div>
          ) : null}

          <motion.section
            variants={sectionVariants}
            initial="hidden"
            animate="visible"
            className="grid grid-cols-1 gap-6 md:grid-cols-[1.4fr_0.6fr]"
          >
            <div className="rounded-[2rem] bg-[linear-gradient(135deg,rgba(255,255,255,0.04)_0%,rgba(20,27,43,0.65)_100%)] p-8 backdrop-blur-[20px]">
              <div className="mb-4 text-xs font-bold uppercase tracking-[0.24em] text-primary">
                Daily Fueling Target
              </div>
              <div className="flex items-end gap-3">
                <div className="font-headline text-7xl font-black tracking-[-0.06em] text-white">
                  {goalSummary.dailyTarget}
                </div>
                <div className="mb-3 text-3xl font-bold text-on-surface-variant">
                  kcal
                </div>
              </div>
              <p className="mt-5 max-w-lg text-lg leading-relaxed text-on-surface-variant">
                Adjusted for your activity level to support sustainable progress
                without unnecessary energy crashes.
              </p>

              <div className="mt-8 grid grid-cols-2 gap-4">
                <div className="rounded-2xl bg-surface-container-low/70 p-5">
                  <div className="mb-1 text-[11px] font-bold uppercase tracking-[0.22em] text-primary">
                    TDEE
                  </div>
                  <div className="text-3xl font-black text-white">
                    {goalSummary.tdee}
                  </div>
                </div>

                <div className="rounded-2xl bg-surface-container-low/70 p-5">
                  <div className="mb-1 text-[11px] font-bold uppercase tracking-[0.22em] text-secondary">
                    BMR
                  </div>
                  <div className="text-3xl font-black text-white">
                    {goalSummary.bmr}
                  </div>
                </div>
              </div>
            </div>

            <div className="flex flex-col gap-4">
              <Button
                type="button"
                variant="ghost"
                onClick={() => router.push("/personal-details")}
                className="rounded-full bg-surface-container-highest/60 py-7 text-on-surface hover:bg-surface-container-high"
              >
                Back
              </Button>

              <Button
                type="submit"
                disabled={saveGoalSetupMutation.isPending}
                className="rounded-full py-7 shadow-[0_0_20px_rgba(78,222,163,0.2)]"
              >
                {saveGoalSetupMutation.isPending ? (
                  <LoadingState label="Saving goals..." className="text-on-primary" />
                ) : (
                  "Continue"
                )}
              </Button>
            </div>
          </motion.section>
        </form>
      </div>
    </div>
  );
}