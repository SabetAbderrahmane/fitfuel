"use client";

import { motion } from "framer-motion";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Flag, Target, TrendingDown } from "lucide-react";

import { recentMetrics, weightTrendData } from "@/features/progress/data/progress.mock";

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

export function WeightGoalPage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      className="space-y-8"
    >
      <div className="grid grid-cols-1 gap-8 xl:grid-cols-[1.3fr_0.7fr]">
        <GlassCard className="relative overflow-hidden">
          <div className="pointer-events-none absolute right-0 top-0 h-full w-1/2 opacity-20">
            <div className="h-full w-full bg-gradient-to-l from-primary to-transparent" />
          </div>

          <div className="relative">
            <div className="flex items-center gap-2 text-[11px] font-black uppercase tracking-[0.24em] text-primary">
              <Target className="h-4 w-4" />
              Weight Goal
            </div>

            <h1 className="mt-4 font-headline text-4xl font-extrabold tracking-tight text-white">
              Cut cleaner. Land lighter.
            </h1>

            <p className="mt-3 max-w-2xl text-lg leading-relaxed text-slate-400">
              A focused view of your current body-weight trajectory, target pace, and
              upcoming milestones.
            </p>

            <div className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-4">
              {[
                { label: "Current", value: "84.2kg" },
                { label: "Target", value: "82.0kg" },
                { label: "Weekly Rate", value: "-0.45kg" },
                { label: "ETA", value: "5 weeks" },
              ].map((item) => (
                <div
                  key={item.label}
                  className="rounded-2xl border border-white/5 bg-white/[0.03] p-4"
                >
                  <div className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">
                    {item.label}
                  </div>
                  <div className="mt-2 font-headline text-2xl font-black text-white">
                    {item.value}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </GlassCard>

        <GlassCard>
          <div className="flex items-center gap-2 text-[11px] font-black uppercase tracking-[0.24em] text-secondary">
            <Flag className="h-4 w-4" />
            Milestones
          </div>

          <div className="mt-6 space-y-5">
            {[
              { label: "Sub-84.0kg", status: "Very close", done: false },
              { label: "18% body fat", status: "2 checkpoints away", done: false },
              { label: "11-day streak", status: "Locked in", done: true },
            ].map((milestone) => (
              <div
                key={milestone.label}
                className="rounded-2xl border border-white/5 bg-white/[0.03] p-4"
              >
                <div className="font-bold text-white">{milestone.label}</div>
                <div
                  className={`mt-2 text-xs font-black uppercase tracking-[0.18em] ${
                    milestone.done ? "text-primary" : "text-secondary"
                  }`}
                >
                  {milestone.status}
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>

      <div className="grid grid-cols-1 gap-8 xl:grid-cols-[1.2fr_0.8fr]">
        <GlassCard>
          <div className="mb-6">
            <h2 className="font-headline text-2xl font-bold text-white">
              Goal Trajectory
            </h2>
            <p className="text-sm text-slate-400">
              Current pace vs target line
            </p>
          </div>

          <div className="h-[340px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={weightTrendData}>
                <defs>
                  <linearGradient id="weightArea" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="0%" stopColor="#4edea3" stopOpacity={0.4} />
                    <stop offset="100%" stopColor="#4edea3" stopOpacity={0.02} />
                  </linearGradient>
                </defs>

                <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis
                  dataKey="label"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "#86948a", fontSize: 11, fontWeight: 700 }}
                />
                <YAxis hide domain={["dataMin - 1", "dataMax + 1"]} />
                <Tooltip
                  contentStyle={{
                    background: "#141b2b",
                    border: "1px solid rgba(255,255,255,0.08)",
                    borderRadius: "12px",
                    color: "#dce2f7",
                  }}
                />
                <ReferenceLine
                  y={82}
                  stroke="#ffb95f"
                  strokeDasharray="4 4"
                  strokeOpacity={0.45}
                />
                <Area
                  dataKey="value"
                  stroke="#4edea3"
                  fill="url(#weightArea)"
                  strokeWidth={3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        <GlassCard>
          <div className="mb-6 flex items-center gap-2 text-[11px] font-black uppercase tracking-[0.24em] text-primary">
            <TrendingDown className="h-4 w-4" />
            Recent Weigh-ins
          </div>

          <div className="space-y-4">
            {recentMetrics.map((item) => (
              <div
                key={item.date}
                className="flex items-center justify-between rounded-2xl border border-white/5 bg-white/[0.03] px-5 py-4"
              >
                <div>
                  <div className="text-sm font-bold text-white">{item.date}</div>
                  <div className="mt-1 text-[10px] font-black uppercase tracking-[0.18em] text-slate-500">
                    Body fat {item.bodyFat}%
                  </div>
                </div>

                <div className="text-right">
                  <div className="font-headline text-2xl font-black text-white">
                    {item.weight}
                  </div>
                  <div className="text-[10px] font-black uppercase tracking-[0.18em] text-primary">
                    kg
                  </div>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </motion.div>
  );
}