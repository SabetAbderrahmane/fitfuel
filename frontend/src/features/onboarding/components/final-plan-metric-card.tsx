"use client";

import { motion } from "framer-motion";

type FinalPlanMetricCardProps = {
  title: string;
  value: string;
  subtitle: string;
  percentage: number;
  color: string;
};

export function FinalPlanMetricCard({
  title,
  value,
  subtitle,
  percentage,
  color,
}: Readonly<FinalPlanMetricCardProps>) {
  const radius = 30;
  const circumference = 2 * Math.PI * radius;

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -4 }}
      className="group relative overflow-hidden rounded-lg bg-[rgba(46,53,69,0.6)] p-6 shadow-[0_20px_60px_rgba(0,0,0,0.3)] transition-all duration-500 backdrop-blur-[24px]"
    >
      <div className="absolute inset-0 opacity-0 transition-opacity duration-500 group-hover:opacity-5" style={{ backgroundColor: color }} />

      <div className="relative z-10 space-y-1">
        <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-on-surface-variant/60 transition-colors group-hover:text-on-surface">
          {title}
        </h3>
        <div className="origin-left text-4xl font-headline font-extrabold tracking-tight text-white transition-transform duration-500 group-hover:scale-105">
          {value}
        </div>
        <div className="text-[11px] font-medium text-on-surface-variant/40">
          {subtitle}
        </div>
      </div>

      <div className="relative z-10 h-20 w-20 overflow-visible">
        <svg className="h-full w-full -rotate-90 overflow-visible">
          <circle
            cx="40"
            cy="40"
            r={radius}
            fill="transparent"
            stroke="currentColor"
            strokeWidth="6"
            className="text-surface-container-highest"
          />
          <motion.circle
            initial={{ pathLength: 0, opacity: 0.2 }}
            animate={{
              pathLength: percentage / 100,
              opacity: [1, 0.4, 1],
            }}
            transition={{
              pathLength: { duration: 2, ease: "easeOut" },
              opacity: { duration: 3, repeat: Infinity, ease: "easeInOut" },
            }}
            cx="40"
            cy="40"
            r={radius}
            fill="transparent"
            stroke={color}
            strokeWidth="6"
            strokeDasharray={circumference}
            strokeLinecap="round"
          />
        </svg>

        <div
          className="absolute inset-0 flex items-center justify-center text-[10px] font-black tracking-tighter"
          style={{ color }}
        >
          {percentage}%
        </div>
      </div>

      <div className="absolute inset-0 rounded-lg border border-white/0 transition-colors duration-500 group-hover:border-white/10" />
    </motion.div>
  );
}