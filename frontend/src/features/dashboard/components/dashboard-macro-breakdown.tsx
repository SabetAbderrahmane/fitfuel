"use client";

import { motion } from "framer-motion";

type MacroBarProps = {
  label: string;
  current: number;
  target: number;
  color: string;
  delay: number;
};

function MacroBar({
  label,
  current,
  target,
  color,
  delay,
}: Readonly<MacroBarProps>) {
  const safeTarget = Math.max(target, 1);
  const percentage = Math.min((current / safeTarget) * 100, 100);

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay, duration: 0.5 }}
      className="group/bar space-y-2"
    >
      <div className="flex justify-between text-xs font-bold">
        <span className="uppercase tracking-wider text-muted-foreground transition-colors group-hover/bar:text-heading">
          {label}
        </span>
        <span className="text-heading">
          <span style={{ color }}>{Math.round(current)}g</span>
          <span className="font-normal text-muted-foreground">
            {" "}
            / {Math.round(target)}g
          </span>
        </span>
      </div>

      <div className="h-2 overflow-hidden rounded-full bg-surface-high">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{
            delay: delay + 0.3,
            duration: 1.2,
            ease: [0.34, 1.56, 0.64, 1],
          }}
          className="h-full rounded-full"
          style={{
            backgroundColor: color,
            boxShadow: `0 0 12px ${color}4d`,
          }}
        />
      </div>
    </motion.div>
  );
}

type DashboardMacroBreakdownProps = {
  protein: { current: number; target: number };
  carbs: { current: number; target: number };
  fats: { current: number; target: number };
};

export function DashboardMacroBreakdown({
  protein,
  carbs,
  fats,
}: Readonly<DashboardMacroBreakdownProps>) {
  return (
    <motion.div
      whileHover={{ y: -5, rotateX: -1, rotateY: 2 }}
      style={{ perspective: 1000 }}
      className="dashboard-kinetic-card group h-full space-y-8 rounded-2xl p-8"
    >
      <div className="pointer-events-none absolute inset-0 bg-white/[0.02] opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
      <h3 className="relative z-10 font-display text-lg font-black text-heading">
        Macro Breakdown
      </h3>

      <div className="relative z-10 space-y-6">
        <MacroBar
          label="Protein"
          current={protein.current}
          target={protein.target}
          color="#4EDEA3"
          delay={0.6}
        />
        <MacroBar
          label="Carbs"
          current={carbs.current}
          target={carbs.target}
          color="#FFB95F"
          delay={0.7}
        />
        <MacroBar
          label="Fats"
          current={fats.current}
          target={fats.target}
          color="#ADC6FF"
          delay={0.8}
        />
      </div>
    </motion.div>
  );
}