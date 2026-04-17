"use client";

import { motion } from "framer-motion";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { CheckCircle2, Droplets, Plus, Waves } from "lucide-react";

import { hydrationTrendData, waterSchedule } from "@/features/progress/data/progress.mock";

function GlassCard({
  children,
  className = "",
}: Readonly<{
  children: React.ReactNode;
  className?: string;
}>) {
  return (
    <div
      className={`rounded-2xl border border-white/5 bg-[#141b2b]/85 p-8 shadow-[0_20px_50px_rgba(0,0,0,0.28)] backdrop-blur-xl ${className}`}
    >
      {children}
    </div>
  );
}

export function WaterIntakePage() {
  const targetLiters = 3.2;
  const currentLiters = 2.4;
  const pct = Math.min((currentLiters / targetLiters) * 100, 100);

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      className="space-y-8"
    >
      <div className="grid grid-cols-1 gap-8 xl:grid-cols-[1.15fr_0.85fr]">
        <GlassCard className="relative overflow-hidden">
          <div className="pointer-events-none absolute right-[-10%] top-[-10%] h-72 w-72 rounded-full bg-primary/10 blur-[90px]" />

          <div className="flex items-center gap-2 text-[11px] font-black uppercase tracking-[0.24em] text-primary">
            <Droplets className="h-4 w-4" />
            Hydration
          </div>

          <h1 className="mt-4 font-headline text-4xl font-extrabold tracking-tight text-white">
            Hydrate sharper.
          </h1>

          <p className="mt-3 max-w-2xl text-lg leading-relaxed text-slate-400">
            Frontend-only hydration screen for now. You’ll plug in the real backend
            and model later.
          </p>

          <div className="mt-8 flex flex-wrap gap-4">
            {["250ml", "500ml", "750ml", "1L"].map((value) => (
              <button
                key={value}
                className="flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-5 py-3 text-sm font-black text-primary transition-all hover:scale-[1.02]"
              >
                <Plus className="h-4 w-4" />
                {value}
              </button>
            ))}
          </div>
        </GlassCard>

        <GlassCard className="flex flex-col items-center justify-center text-center">
          <div className="relative h-56 w-56">
            <svg className="h-full w-full -rotate-90">
              <circle
                cx="112"
                cy="112"
                r="94"
                fill="transparent"
                stroke="rgba(255,255,255,0.08)"
                strokeWidth="16"
              />
              <motion.circle
                cx="112"
                cy="112"
                r="94"
                fill="transparent"
                stroke="#4edea3"
                strokeWidth="16"
                strokeLinecap="round"
                strokeDasharray={2 * Math.PI * 94}
                initial={{ strokeDashoffset: 2 * Math.PI * 94 }}
                animate={{
                  strokeDashoffset:
                    2 * Math.PI * 94 - ((2 * Math.PI * 94) * pct) / 100,
                }}
                transition={{ duration: 1.2, ease: "easeOut" }}
              />
            </svg>

            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <div className="font-headline text-5xl font-black text-white">
                {currentLiters.toFixed(1)}L
              </div>
              <div className="mt-2 text-xs font-black uppercase tracking-[0.22em] text-primary">
                of {targetLiters.toFixed(1)}L
              </div>
            </div>
          </div>
        </GlassCard>
      </div>

      <div className="grid grid-cols-1 gap-8 xl:grid-cols-[1.1fr_0.9fr]">
        <GlassCard>
          <div className="mb-6">
            <h2 className="font-headline text-2xl font-bold text-white">
              Weekly Intake Trend
            </h2>
            <p className="text-sm text-slate-400">
              Mock hydration data until backend is ready
            </p>
          </div>

          <div className="h-[320px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={hydrationTrendData}>
                <defs>
                  <linearGradient id="hydrationArea" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="0%" stopColor="#4edea3" stopOpacity={0.4} />
                    <stop offset="100%" stopColor="#4edea3" stopOpacity={0.03} />
                  </linearGradient>
                </defs>

                <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis
                  dataKey="day"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "#86948a", fontSize: 11, fontWeight: 700 }}
                />
                <YAxis hide />
                <Tooltip
                  contentStyle={{
                    background: "#141b2b",
                    border: "1px solid rgba(255,255,255,0.08)",
                    borderRadius: "12px",
                    color: "#dce2f7",
                  }}
                />
                <Area
                  dataKey="liters"
                  stroke="#4edea3"
                  fill="url(#hydrationArea)"
                  strokeWidth={3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        <GlassCard>
          <div className="mb-6 flex items-center gap-2 text-[11px] font-black uppercase tracking-[0.24em] text-secondary">
            <Waves className="h-4 w-4" />
            Schedule
          </div>

          <div className="space-y-4">
            {waterSchedule.map((item) => (
              <div
                key={`${item.time}-${item.label}`}
                className="flex items-center justify-between rounded-2xl border border-white/5 bg-white/[0.03] px-5 py-4"
              >
                <div>
                  <div className="text-sm font-bold text-white">{item.label}</div>
                  <div className="mt-1 text-[10px] font-black uppercase tracking-[0.18em] text-slate-500">
                    {item.time}
                  </div>
                </div>
                

                <div className="flex items-center gap-3">
                  <span className="text-sm font-bold text-primary">{item.amount}</span>
                  {item.done ? (
                    <CheckCircle2 className="h-5 w-5 text-primary" />
                  ) : (
                    <div className="h-5 w-5 rounded-full border border-white/10" />
                  )}
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </motion.div>
  );
}