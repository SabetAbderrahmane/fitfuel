"use client";

import { motion } from "framer-motion";

type MacroPrecisionProps = {
  proteinG: number;
  carbsG: number;
  fatG: number;
};

function MacroItem({
  label,
  value,
  percentage,
  color,
  description,
  isMain,
}: Readonly<{
  label: string;
  value: number;
  percentage: number;
  color: string;
  description: string;
  isMain?: boolean;
}>) {
  return (
    <div className="group/item space-y-4">
      <div className="flex items-end justify-between">
        <div className="flex flex-col">
          <span className="mb-1 text-[10px] font-black uppercase tracking-[0.2em] text-on-surface-variant/50 transition-colors group-hover/item:text-on-surface">
            {label}
          </span>
          <span className="origin-left text-4xl font-headline font-black tracking-tighter text-white transition-transform group-hover/item:scale-105">
            {value}
            <span className="ml-1 text-xs font-medium text-on-surface-variant/40">
              g
            </span>
          </span>
        </div>

        <span
          className="text-lg font-black tracking-tighter transition-all group-hover/item:drop-shadow-[0_0_8px_currentColor]"
          style={{ color }}
        >
          {percentage}%
        </span>
      </div>

      <div className={`relative w-full overflow-hidden rounded-full bg-surface-container-highest ${isMain ? "h-5" : "h-3"}`}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 1.5, ease: "easeOut", delay: 0.5 }}
          className="relative h-full"
          style={{ backgroundColor: color }}
        >
          <div className="absolute inset-0 -translate-x-full animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-white/20 to-transparent" />
        </motion.div>
      </div>

      <p className="max-w-[200px] text-[11px] font-medium leading-relaxed text-on-surface-variant/40 transition-colors group-hover/item:text-on-surface-variant/70">
        {description}
      </p>
    </div>
  );
}

export function FinalPlanMacroPrecision({
  proteinG,
  carbsG,
  fatG,
}: Readonly<MacroPrecisionProps>) {
  const proteinCalories = proteinG * 4;
  const carbsCalories = carbsG * 4;
  const fatCalories = fatG * 9;
  const totalCalories = proteinCalories + carbsCalories + fatCalories || 1;

  const proteinPct = Math.round((proteinCalories / totalCalories) * 100);
  const carbsPct = Math.round((carbsCalories / totalCalories) * 100);
  const fatPct = Math.max(0, 100 - proteinPct - carbsPct);

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
      className="group relative overflow-hidden rounded-lg bg-[rgba(46,53,69,0.6)] p-10 shadow-[0_0_80px_rgba(0,0,0,0.2)] transition-all duration-700 hover:shadow-[0_0_100px_rgba(0,0,0,0.4)] backdrop-blur-[24px]"
    >
      <div className="absolute -left-24 -top-24 h-64 w-64 rounded-full bg-primary/5 blur-[100px] transition-colors duration-700 group-hover:bg-primary/10" />
      <div className="absolute -bottom-24 -right-24 h-64 w-64 rounded-full bg-secondary/5 blur-[100px] transition-colors duration-700 group-hover:bg-secondary/10" />

      <div className="relative z-10 mb-12 flex flex-col justify-between gap-6 md:flex-row md:items-start">
        <div className="space-y-2">
          <h2 className="font-headline text-3xl font-black tracking-tight text-white">
            Macro Precision
          </h2>
          <p className="max-w-md text-sm font-medium text-on-surface-variant/60">
            Targeted nutrient density for muscle synthesis and metabolic health.
          </p>
        </div>

        <div className="flex gap-8">
          {[
            { label: "Protein", color: "#4edea3" },
            { label: "Carbs", color: "#ffb95f" },
            { label: "Fats", color: "#adc6ff" },
          ].map((item) => (
            <div key={item.label} className="flex items-center gap-3">
              <div
                className="h-2 w-2 rounded-full"
                style={{
                  backgroundColor: item.color,
                  boxShadow: `0 0 10px ${item.color}`,
                }}
              />
              <span className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant/80">
                {item.label}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-16 md:grid-cols-3">
        <MacroItem
          label="Protein"
          value={proteinG}
          percentage={proteinPct}
          color="#4edea3"
          description="Essential for muscle recovery and metabolic rate support."
          isMain
        />
        <MacroItem
          label="Carbs"
          value={carbsG}
          percentage={carbsPct}
          color="#ffb95f"
          description="Primary energy source for intense training sessions."
        />
        <MacroItem
          label="Fats"
          value={fatG}
          percentage={fatPct}
          color="#adc6ff"
          description="Hormonal balance and vital nutrient absorption."
        />
      </div>
    </motion.div>
  );
}