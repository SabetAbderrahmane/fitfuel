"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Flame, Leaf, ShieldCheck, SlidersHorizontal } from "lucide-react";

import { cn } from "@/lib/utils/cn";

function GlassCard({
  children,
  className = "",
}: Readonly<{
  children: React.ReactNode;
  className?: string;
}>) {
  return (
    <div
      className={cn(
        "rounded-[2rem] border border-white/5 bg-[#141f34]/90 p-6 shadow-[0_20px_60px_rgba(0,0,0,0.28)] backdrop-blur-xl md:p-8",
        className
      )}
    >
      {children}
    </div>
  );
}

export function GoalsPreferencesSettingsPage() {
  const [goal, setGoal] = useState("Weight Loss");
  const [calories, setCalories] = useState(1362);
  const [protein, setProtein] = useState(152);
  const [carbs, setCarbs] = useState(51);
  const [fat, setFat] = useState(61);

  const goalOptions = [
    "Weight Loss",
    "Maintenance",
    "Muscle Gain",
    "Recomposition",
  ];

  const chipBase =
    "rounded-full px-4 py-2 text-sm font-black transition-all";

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      className="space-y-8"
    >
      <section>
        <h1 className="font-headline text-4xl font-extrabold tracking-tight text-white md:text-5xl">
          Goals & Preferences
        </h1>
        <p className="mt-3 max-w-3xl text-lg text-slate-400">
          Tune your calorie targets, nutrition preferences, and dietary filters.
        </p>
      </section>

      <div className="grid grid-cols-1 gap-8 xl:grid-cols-[1.1fr_0.9fr]">
        <GlassCard>
          <div className="mb-6 flex items-center gap-2 text-[11px] font-black uppercase tracking-[0.24em] text-primary">
            <Flame className="h-4 w-4" />
            Active Goal
          </div>

          <div className="flex flex-wrap gap-3">
            {goalOptions.map((option) => (
              <button
                key={option}
                onClick={() => setGoal(option)}
                className={cn(
                  chipBase,
                  goal === option
                    ? "bg-primary text-[#072516] shadow-[0_8px_18px_rgba(78,222,163,0.24)]"
                    : "bg-white/[0.04] text-slate-300"
                )}
              >
                {option}
              </button>
            ))}
          </div>

          <div className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-4">
            {[
              {
                label: "Calories",
                value: calories,
                setValue: setCalories,
              },
              {
                label: "Protein",
                value: protein,
                setValue: setProtein,
              },
              {
                label: "Carbs",
                value: carbs,
                setValue: setCarbs,
              },
              {
                label: "Fat",
                value: fat,
                setValue: setFat,
              },
            ].map((item) => (
              <div
                key={item.label}
                className="rounded-2xl border border-white/5 bg-[#0d1830] p-4"
              >
                <div className="text-[10px] font-black uppercase tracking-[0.18em] text-slate-500">
                  {item.label}
                </div>
                <input
                  type="number"
                  value={item.value}
                  onChange={(event) =>
                    item.setValue(Number(event.target.value) || 0)
                  }
                  className="mt-3 w-full bg-transparent text-3xl font-black text-white outline-none"
                />
              </div>
            ))}
          </div>

          <div className="mt-8 flex justify-end">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="rounded-full bg-primary px-8 py-3 text-base font-black text-[#062315]"
            >
              Save Preferences
            </motion.button>
          </div>
        </GlassCard>

        <div className="space-y-8">
          <GlassCard>
            <div className="mb-5 flex items-center gap-2 text-[11px] font-black uppercase tracking-[0.24em] text-secondary">
              <Leaf className="h-4 w-4" />
              Dietary Style
            </div>

            <div className="flex flex-wrap gap-3">
              {["High Protein", "Halal", "Low Sugar", "Mediterranean"].map(
                (tag) => (
                  <button
                    key={tag}
                    className="rounded-full border border-secondary/20 bg-secondary/10 px-4 py-2 text-sm font-black text-secondary"
                  >
                    {tag}
                  </button>
                )
              )}
            </div>
          </GlassCard>

          <GlassCard>
            <div className="mb-5 flex items-center gap-2 text-[11px] font-black uppercase tracking-[0.24em] text-primary">
              <ShieldCheck className="h-4 w-4" />
              Restrictions
            </div>

            <div className="space-y-3 text-base text-slate-300">
              <div className="rounded-2xl bg-white/[0.03] px-4 py-3">No peanuts</div>
              <div className="rounded-2xl bg-white/[0.03] px-4 py-3">No shellfish</div>
              <div className="rounded-2xl bg-white/[0.03] px-4 py-3">Avoid deep-fried meals</div>
            </div>
          </GlassCard>

          <GlassCard>
            <div className="mb-5 flex items-center gap-2 text-[11px] font-black uppercase tracking-[0.24em] text-slate-300">
              <SlidersHorizontal className="h-4 w-4" />
              AI Planning Style
            </div>

            <div className="space-y-4">
              {[
                "Prefer variety over strict repetition",
                "Keep prep time under 20 minutes",
                "Bias recommendations toward lean meals",
              ].map((item) => (
                <label
                  key={item}
                  className="flex items-center justify-between rounded-2xl bg-white/[0.03] px-4 py-4"
                >
                  <span className="font-medium text-white">{item}</span>
                  <div className="h-6 w-11 rounded-full bg-primary/30 p-1">
                    <div className="ml-auto h-4 w-4 rounded-full bg-primary" />
                  </div>
                </label>
              ))}
            </div>
          </GlassCard>
        </div>
      </div>
    </motion.div>
  );
}