"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { UserCircle, Flame, Activity, Zap } from "lucide-react";

import { Button } from "@/components/ui/button";
import { FinalPlanMetricCard } from "@/features/onboarding/components/final-plan-metric-card";
import { FinalPlanMacroPrecision } from "@/features/onboarding/components/final-plan-macro-precision";
import type { FinalGoalSummary } from "@/features/onboarding/types/final-plan.types";

export function FinalPlanSummary({
  summary,
}: Readonly<{
  summary: FinalGoalSummary;
}>) {
  const router = useRouter();

  const targetCalories = summary.target_calories;
  const estimatedTdee = summary.estimated_tdee ?? 0;
  const estimatedBmr = summary.estimated_bmr ?? 0;

  const tdeeRatio =
    estimatedTdee > 0
      ? Math.min(100, Math.max(1, Math.round((targetCalories / estimatedTdee) * 100)))
      : 0;

  const bmrRatio =
    estimatedTdee > 0 && estimatedBmr > 0
      ? Math.min(100, Math.max(1, Math.round((estimatedBmr / estimatedTdee) * 100)))
      : 0;

  return (
    <div className="relative z-10 mx-auto w-full max-w-5xl space-y-12">
      <motion.header
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative overflow-hidden rounded-lg bg-gradient-to-br from-primary-container via-primary-container to-surface-container-low p-12 shadow-[0_40px_100px_rgba(0,0,0,0.3)] md:p-16"
      >
        <div className="absolute -right-32 -top-32 h-96 w-96 animate-pulse rounded-full bg-primary/30 blur-[120px]" />
        <div className="absolute -bottom-20 -left-20 h-64 w-64 rounded-full bg-secondary/10 blur-[80px]" />

        <div className="relative z-10 space-y-6">
          <h1 className="font-headline text-5xl font-black uppercase leading-[0.9] tracking-tighter text-white md:text-7xl">
            You've got this!
            <br />
            <span className="text-on-primary-fixed opacity-90">
              Your plan is ready.
            </span>
          </h1>

          <p className="max-w-xl text-xl font-medium leading-relaxed text-on-primary-container opacity-80">
            Based on your biometrics and goals, we've engineered a precise nutritional path for your transformation.
          </p>
        </div>
      </motion.header>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-12">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          whileHover={{ scale: 1.01, y: -4 }}
          transition={{ delay: 0.1 }}
          className="group relative overflow-hidden rounded-lg bg-[rgba(46,53,69,0.6)] p-10 shadow-[0_40px_80px_rgba(0,0,0,0.2)] transition-all duration-500 hover:shadow-[0_40px_100px_rgba(78,222,163,0.1)] backdrop-blur-[24px] md:col-span-8"
        >
          <motion.div
            animate={{ opacity: [0, 0.05, 0] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
            className="pointer-events-none absolute inset-0 bg-primary/20"
          />

          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 transition-opacity duration-700 group-hover:opacity-100" />

          <div className="absolute -bottom-8 -right-8 opacity-5 transition-all duration-700 group-hover:rotate-12 group-hover:scale-110 group-hover:opacity-10">
            <Flame className="h-[240px] w-[240px] text-primary" />
          </div>

          <span className="relative z-10 mb-4 text-[10px] font-black uppercase tracking-[0.3em] text-primary transition-all duration-500 group-hover:tracking-[0.4em]">
            Daily Fueling Target
          </span>

          <div className="relative z-10 flex items-baseline gap-6">
            <span className="font-headline text-8xl font-black leading-none tracking-tighter text-white transition-all duration-500 group-hover:drop-shadow-[0_0_20px_rgba(255,255,255,0.2)] md:text-[10rem]">
              {targetCalories.toLocaleString()}
            </span>
            <span className="font-headline text-3xl font-extrabold uppercase tracking-tighter text-on-surface-variant/40 transition-colors duration-500 group-hover:text-primary/40">
              kcal
            </span>
          </div>

          <p className="relative z-10 mt-8 max-w-md text-sm font-medium leading-relaxed text-on-surface-variant/60 transition-colors duration-500 group-hover:text-on-surface-variant/80">
            Adjusted for your activity level to ensure consistent progress without energy crashes.
          </p>

          <div className="absolute right-0 top-0 h-32 w-32 bg-gradient-to-bl from-primary/20 to-transparent opacity-0 transition-opacity duration-700 group-hover:opacity-100" />
        </motion.div>

        <div className="space-y-6 md:col-span-4">
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <FinalPlanMetricCard
              title="TDEE"
              value={estimatedTdee ? Math.round(estimatedTdee).toLocaleString() : "—"}
              subtitle="Expended Daily"
              percentage={tdeeRatio}
              color="#ffb95f"
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <FinalPlanMetricCard
              title="BMR"
              value={estimatedBmr ? Math.round(estimatedBmr).toLocaleString() : "—"}
              subtitle="Basal Metabolism"
              percentage={bmrRatio}
              color="#adc6ff"
            />
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="md:col-span-12"
        >
          <FinalPlanMacroPrecision
            proteinG={summary.target_protein_g}
            carbsG={summary.target_carbs_g}
            fatG={summary.target_fat_g}
          />
        </motion.div>
      </div>

      <div className="flex flex-col items-center space-y-8 pb-24 pt-16">
        <Button
          size="lg"
          onClick={() => router.push("/dashboard")}
          className="group relative overflow-hidden rounded-full bg-primary px-16 py-10 font-headline text-2xl font-black text-on-primary shadow-[0_20px_50px_rgba(78,222,163,0.3)] transition-all duration-500 hover:shadow-[0_30px_70px_rgba(78,222,163,0.5)] active:scale-95"
        >
          <span className="relative z-10">Continue to Dashboard</span>
          <div className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/20 to-transparent transition-transform duration-1000 group-hover:translate-x-full" />
          <div className="absolute inset-0 rounded-full border-4 border-primary/30 opacity-0 transition-all duration-500 group-hover:scale-110 group-hover:opacity-100" />
        </Button>

        <p className="text-xs font-bold uppercase tracking-[0.2em] text-on-surface-variant/40">
          You can adjust your preferences any time in settings.
        </p>
      </div>
    </div>
  );
}