"use client";

import { motion } from "framer-motion";

type DashboardCalorieHeroProps = {
  consumedCalories: number;
  targetCalories: number;
};

export function DashboardCalorieHero({
  consumedCalories,
  targetCalories,
}: Readonly<DashboardCalorieHeroProps>) {
  const safeTarget = Math.max(targetCalories, 1);
  const progress = Math.min((consumedCalories / safeTarget) * 100, 100);
  const remainingCalories = Math.max(targetCalories - consumedCalories, 0);

  const strokeWidth = 12;
  const radius = 80;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (progress / 100) * circumference;

  return (
    <motion.div
      whileHover={{ y: -5, rotateX: 2, rotateY: 1 }}
      style={{ perspective: 1000 }}
      className="dashboard-kinetic-card group relative flex items-center gap-8 rounded-2xl p-8"
    >
      <motion.div
        className="absolute inset-0 bg-primary/5 opacity-0 transition-opacity duration-700 group-hover:opacity-100"
        initial={false}
      />

      <div className="relative flex h-48 w-48 items-center justify-center">
        <svg className="dashboard-progress-ring h-full w-full overflow-visible">
          <circle
            cx="96"
            cy="96"
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            fill="transparent"
            className="text-surface-high"
          />
          <motion.circle
            cx="96"
            cy="96"
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 2, ease: [0.34, 1.56, 0.64, 1] }}
            className="dashboard-glow-green text-primary"
            strokeLinecap="butt"
          />
        </svg>

        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="font-display text-4xl font-black tracking-tighter text-heading">
            {consumedCalories.toLocaleString()}
          </span>
          <span className="mt-1 text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground">
            / {targetCalories.toLocaleString()} kcal
          </span>
        </div>
      </div>

      <div className="relative z-10 flex-1 space-y-4">
        <div>
          <h1 className="font-display text-4xl font-black leading-[1.1] tracking-tight text-heading">
            Fueling Your
            <br />
            <span className="dashboard-glow-green text-primary">Performance</span>
          </h1>
        </div>

        <p className="max-w-xs text-sm font-medium leading-relaxed text-foreground">
          You&apos;ve consumed{" "}
          <span className="font-black text-heading">
            {Math.round(progress)}%
          </span>{" "}
          of your daily target.{" "}
          {remainingCalories > 0
            ? `${remainingCalories.toLocaleString()} kcal remaining to reach your metabolic peak.`
            : "You have already reached your calorie target for today."}
        </p>

        <div className="flex gap-3">
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="rounded-full border border-primary/20 bg-primary/10 px-4 py-2 text-xs font-black text-primary"
          >
            {remainingCalories.toLocaleString()} kcal Left
          </motion.div>

          <motion.div
            whileHover={{ scale: 1.05 }}
            className="rounded-full border border-white/5 bg-surface-high px-4 py-2 text-xs font-black text-heading"
          >
            Active Day
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}