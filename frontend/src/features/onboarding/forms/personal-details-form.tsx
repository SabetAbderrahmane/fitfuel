"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion, type Variants } from "framer-motion";
import {
  Activity,
  Armchair,
  ArrowLeft,
  ArrowRight,
  Calendar,
  Dumbbell,
  Flame,
  Footprints,
  Ruler,
  Users,
  Weight,
  Zap,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { useProfileQuery } from "@/features/onboarding/hooks/use-profile-query";
import { useUpsertProfileMutation } from "@/features/onboarding/hooks/use-upsert-profile-mutation";
import {
  personalDetailsSchema,
  type PersonalDetailsFormValues,
} from "@/features/onboarding/schemas/personal-details.schema";
import type { ActivityLevel } from "@/features/onboarding/types/profile.types";
import { cn } from "@/lib/utils/cn";

const activityLevels: Array<{
  id: ActivityLevel;
  label: string;
  icon: typeof Armchair;
}> = [
  { id: "sedentary", label: "Sedentary", icon: Armchair },
  { id: "lightly_active", label: "Lightly Active", icon: Footprints },
  { id: "moderately_active", label: "Moderately Active", icon: Dumbbell },
  { id: "very_active", label: "Very Active", icon: Activity },
  { id: "extra_active", label: "Extra Active", icon: Flame },
];

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.12,
    },
  },
};

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 18 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      type: "spring",
      stiffness: 300,
      damping: 24,
    },
  },
};

export function PersonalDetailsForm({
  accessToken,
}: Readonly<{
  accessToken: string;
}>) {
  const router = useRouter();
  const profileQuery = useProfileQuery(accessToken);
  const upsertProfileMutation = useUpsertProfileMutation();

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    control,
    reset,
    formState: { errors },
  } = useForm<PersonalDetailsFormValues>({
    resolver: zodResolver(personalDetailsSchema),
    defaultValues: {
      age: 25,
      sex: "male",
      heightCm: 182,
      weightKg: 78.5,
      activityLevel: "moderately_active",
    },
  });

  useEffect(() => {
    if (!profileQuery.data) {
      return;
    }

    reset({
      age: profileQuery.data.age ?? 25,
      sex: profileQuery.data.sex === "female" ? "female" : "male",
      heightCm: profileQuery.data.height_cm ?? 182,
      weightKg:
        profileQuery.data.current_weight_kg ??
        profileQuery.data.start_weight_kg ??
        78.5,
      activityLevel:
        (profileQuery.data.activity_profile?.activity_level as
          | ActivityLevel
          | undefined) ?? "moderately_active",
    });
  }, [profileQuery.data, reset]);

  const watchSex = watch("sex");
  const watchActivity = watch("activityLevel");

  const onSubmit = (data: PersonalDetailsFormValues) => {
    const startWeight =
      profileQuery.data?.start_weight_kg && profileQuery.data.start_weight_kg > 0
        ? profileQuery.data.start_weight_kg
        : data.weightKg;

    upsertProfileMutation.mutate(
      {
        accessToken,
        payload: {
          age: data.age,
          sex: data.sex,
          height_cm: data.heightCm,
          start_weight_kg: startWeight,
          current_weight_kg: data.weightKg,
          activity_profile: {
            activity_level: data.activityLevel,
          },
          allergies: [],
          dietary_preferences: [],
        },
      },
      {
        onSuccess: () => {
          router.push("/goals");
        },
      }
    );
  };

  if (profileQuery.isLoading) {
    return (
      <div className="w-full max-w-2xl rounded-[2rem] border border-primary/20 bg-surface-container-low/70 p-10 backdrop-blur-2xl">
        <LoadingState label="Loading your profile..." className="text-primary" />
      </div>
    );
  }

  if (profileQuery.isError) {
    return (
      <div className="w-full max-w-2xl rounded-[2rem] border border-primary/20 bg-surface-container-low/70 p-10 backdrop-blur-2xl">
        <ErrorState message={profileQuery.error.message} />
      </div>
    );
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="w-full max-w-2xl"
    >
      <div className="relative overflow-hidden rounded-[2rem] border border-primary/20 bg-[rgba(25,31,47,0.6)] p-8 shadow-2xl backdrop-blur-[24px] md:p-12">
        <div className="absolute left-0 top-0 h-1.5 w-full bg-surface-container-highest/50">
          <motion.div
            initial={{ width: "25%" }}
            animate={{ width: "50%" }}
            transition={{ duration: 0.9, ease: "circOut" }}
            className="h-full bg-primary shadow-[0_0_15px_rgba(78,222,163,0.5)]"
          />
        </div>

        <motion.div variants={itemVariants} className="mb-10">
          <h2 className="mb-3 font-headline text-4xl font-extrabold tracking-tight text-on-surface md:text-5xl">
            Tell us about <span className="text-primary">yourself</span>
          </h2>
          <p className="max-w-lg text-lg text-on-surface-variant">
            We&apos;ll use these metrics to calculate your personalized fuel and
            training requirements.
          </p>
        </motion.div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-12">
          <motion.div
            variants={itemVariants}
            className="grid grid-cols-1 gap-8 md:grid-cols-2"
          >
            <div className="space-y-3">
              <label className="flex items-center gap-2 font-headline text-sm font-semibold uppercase tracking-wider text-on-surface opacity-70">
                <Calendar className="h-4 w-4 text-primary" />
                Age
              </label>

              <div className="group relative">
                <input
                  type="number"
                  {...register("age", { valueAsNumber: true })}
                  className="h-16 w-full rounded-xl border border-white/5 bg-surface-container-low p-4 font-sans text-xl font-bold text-on-surface transition-all focus:border-primary/50 focus:bg-surface-container-high focus:outline-none"
                />
                <div className="pointer-events-none absolute inset-0 rounded-xl bg-primary/5 opacity-0 transition-opacity group-hover:opacity-100" />
              </div>

              {errors.age ? (
                <p className="text-sm text-[#ffb4ab]">{errors.age.message}</p>
              ) : null}
            </div>

            <div className="space-y-3">
              <label className="flex items-center gap-2 font-headline text-sm font-semibold uppercase tracking-wider text-on-surface opacity-70">
                <Users className="h-4 w-4 text-primary" />
                Biological Sex
              </label>

              <div className="flex h-16 rounded-xl border border-white/5 bg-surface-container-low p-1.5">
                <button
                  type="button"
                  onClick={() => setValue("sex", "male", { shouldValidate: true })}
                  className={cn(
                    "relative flex-1 overflow-hidden rounded-lg px-4 py-2 text-sm font-bold transition-all",
                    watchSex === "male"
                      ? "text-on-primary"
                      : "text-on-surface-variant hover:text-on-surface"
                  )}
                >
                  {watchSex === "male" ? (
                    <motion.div
                      layoutId="sex-toggle"
                      className="absolute inset-0 bg-primary shadow-lg"
                      transition={{ type: "spring", stiffness: 300, damping: 30 }}
                    />
                  ) : null}
                  <span className="relative z-10">Male</span>
                </button>

                <button
                  type="button"
                  onClick={() => setValue("sex", "female", { shouldValidate: true })}
                  className={cn(
                    "relative flex-1 overflow-hidden rounded-lg px-4 py-2 text-sm font-bold transition-all",
                    watchSex === "female"
                      ? "text-on-primary"
                      : "text-on-surface-variant hover:text-on-surface"
                  )}
                >
                  {watchSex === "female" ? (
                    <motion.div
                      layoutId="sex-toggle"
                      className="absolute inset-0 bg-primary shadow-lg"
                      transition={{ type: "spring", stiffness: 300, damping: 30 }}
                    />
                  ) : null}
                  <span className="relative z-10">Female</span>
                </button>
              </div>

              {errors.sex ? (
                <p className="text-sm text-[#ffb4ab]">{errors.sex.message}</p>
              ) : null}
            </div>
          </motion.div>

          <motion.div variants={itemVariants} className="space-y-6">
            <Controller
              name="heightCm"
              control={control}
              render={({ field }) => (
                <>
                  <div className="flex items-end justify-between">
                    <label className="flex items-center gap-2 font-headline text-sm font-semibold uppercase tracking-wider text-on-surface opacity-70">
                      <Ruler className="h-4 w-4 text-primary" />
                      Height
                    </label>

                    <div className="flex items-baseline gap-1">
                      <motion.span
                        key={field.value}
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="font-headline text-4xl font-black text-primary"
                      >
                        {field.value}
                      </motion.span>
                      <span className="text-sm font-bold text-on-surface-variant">
                        cm
                      </span>
                    </div>
                  </div>

                  <Slider
                    value={[field.value]}
                    onValueChange={(value) => field.onChange(value[0])}
                    max={250}
                    min={50}
                    step={1}
                    className="py-4"
                  />
                </>
              )}
            />

            {errors.heightCm ? (
              <p className="text-sm text-[#ffb4ab]">{errors.heightCm.message}</p>
            ) : null}
          </motion.div>

          <motion.div variants={itemVariants} className="space-y-6">
            <Controller
              name="weightKg"
              control={control}
              render={({ field }) => (
                <>
                  <div className="flex items-end justify-between">
                    <label className="flex items-center gap-2 font-headline text-sm font-semibold uppercase tracking-wider text-on-surface opacity-70">
                      <Weight className="h-4 w-4 text-primary" />
                      Current Weight
                    </label>

                    <div className="flex items-baseline gap-1">
                      <motion.span
                        key={field.value}
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="font-headline text-4xl font-black text-primary"
                      >
                        {field.value}
                      </motion.span>
                      <span className="text-sm font-bold text-on-surface-variant">
                        kg
                      </span>
                    </div>
                  </div>

                  <Slider
                    value={[field.value]}
                    onValueChange={(value) => field.onChange(value[0])}
                    max={200}
                    min={30}
                    step={0.5}
                    className="py-4"
                  />
                </>
              )}
            />

            {errors.weightKg ? (
              <p className="text-sm text-[#ffb4ab]">{errors.weightKg.message}</p>
            ) : null}
          </motion.div>

          <motion.div variants={itemVariants} className="space-y-6">
            <label className="flex items-center gap-2 font-headline text-sm font-semibold uppercase tracking-wider text-on-surface opacity-70">
              <Zap className="h-4 w-4 text-primary" />
              Activity Level
            </label>

            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
              {activityLevels.map((level) => {
                const Icon = level.icon;
                const isSelected = watchActivity === level.id;

                return (
                  <motion.button
                    key={level.id}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() =>
                      setValue("activityLevel", level.id, { shouldValidate: true })
                    }
                    type="button"
                    className={cn(
                      "group relative flex flex-col items-center justify-center overflow-hidden rounded-2xl border p-5 text-center transition-all",
                      isSelected
                        ? "border-primary bg-primary/10 shadow-[0_0_20px_rgba(78,222,163,0.15)]"
                        : "border-white/5 bg-surface-container-low hover:border-primary/30 hover:bg-surface-container-high"
                    )}
                  >
                    {isSelected ? (
                      <motion.div
                        layoutId="activity-glow"
                        className="absolute inset-0 bg-primary/5 blur-xl"
                      />
                    ) : null}

                    <Icon
                      className={cn(
                        "mb-3 h-8 w-8 transition-all duration-300",
                        isSelected
                          ? "scale-110 text-primary"
                          : "text-on-surface-variant group-hover:text-primary"
                      )}
                    />

                    <div
                      className={cn(
                        "text-[10px] font-bold uppercase tracking-widest transition-colors",
                        isSelected
                          ? "text-primary"
                          : "text-on-surface-variant group-hover:text-on-surface"
                      )}
                    >
                      {level.label}
                    </div>
                  </motion.button>
                );
              })}
            </div>

            {errors.activityLevel ? (
              <p className="text-sm text-[#ffb4ab]">{errors.activityLevel.message}</p>
            ) : null}
          </motion.div>

          {upsertProfileMutation.isError ? (
            <motion.div
              variants={itemVariants}
              className="rounded-2xl bg-[#ffb4ab]/10 px-4 py-3 text-sm text-[#ffb4ab]"
            >
              {upsertProfileMutation.error.message}
            </motion.div>
          ) : null}

          <motion.div
            variants={itemVariants}
            className="flex flex-col gap-4 pt-8 sm:flex-row"
          >
            <Button
              type="button"
              variant="ghost"
              onClick={() => router.push("/welcome")}
              className="group flex flex-1 items-center justify-center gap-3 rounded-2xl bg-surface-container-highest/50 py-7 font-bold text-on-surface transition-all hover:bg-surface-container-high"
            >
              <ArrowLeft className="h-5 w-5 transition-transform group-hover:-translate-x-1" />
              Back
            </Button>

            <Button
              type="submit"
              disabled={upsertProfileMutation.isPending}
              className="group flex-[2] rounded-2xl bg-primary py-7 font-bold text-on-primary shadow-[0_10px_30px_rgba(78,222,163,0.3)] transition-all hover:-translate-y-1 hover:shadow-[0_15px_40px_rgba(78,222,163,0.4)] active:translate-y-0"
            >
              {upsertProfileMutation.isPending ? (
                <LoadingState label="Saving profile..." className="text-on-primary" />
              ) : (
                <span className="inline-flex items-center gap-3">
                  Continue to Goals
                  <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
                </span>
              )}
            </Button>
          </motion.div>
        </form>
      </div>
    </motion.div>
  );
}