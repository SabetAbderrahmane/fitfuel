"use client";

import { motion } from "framer-motion";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Footprints, Mountain, Timer, Zap } from "lucide-react";

import { stepSessions, stepsTrendData } from "@/features/progress/data/progress.mock";

function GlassCard({
  children,
  className = "",
}: Readonly<{
  children: React.ReactNode;
  className?: string;
}>) {
  return (
    <div
      className={`rounded-2xl border border-white/5 bg-surface-container-low/85 p-8 shadow-[0_20px_50px_rgba(0,0,0,0.28)] backdrop-blur-xl ${className}`}
    >
      {children}
    </div>
  );
}

export function StepsPage() {
  const goal = 12000;
  const current = 8450;
  const pct = Math.min((current / goal) * 100, 100);

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      className="space-y-8"
    >
      <div className="grid grid-cols-1 gap-8 xl:grid-cols-[1.1fr_0.9fr]">
        <GlassCard className="relative overflow-hidden">
          <div className="pointer-events-none absolute right-[-10%] top-[-10%] h-72 w-72 rounded-full bg-secondary/10 blur-[90px]" />

          <div className="flex items-center gap-2 text-[11px] font-black uppercase tracking-[0.24em] text-secondary">
            <Footprints className="h-4 w-4" />
            Steps
          </div>

          <h1 className="mt-4 font-headline text-4xl font-extrabold tracking-tight text-white">
            Move with intention.
          </h1>

          <p className="mt-3 max-w-2xl text-lg leading-relaxed text-slate-400">
            Frontend-only step-tracking UI for now. Backend and sensor/model logic can
            be connected later.
          </p>

          <div className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-4">
            {[
              { label: "Today", value: current.toLocaleString() },
              { label: "Goal", value: goal.toLocaleString() },
              { label: "Distance", value: "6.4 km" },
              { label: "Active Min", value: "61 min" },
            ].map((item) => (
              <div
                key={item.label}
                className="rounded-2xl border border-white/5 bg-white/3 p-4"
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
        </GlassCard>

        <GlassCard>
          <div className="mb-4 text-[11px] font-black uppercase tracking-[0.24em] text-primary">
            Goal Progress
          </div>

          <div className="mb-4 font-headline text-5xl font-black text-white">
            {Math.round(pct)}%
          </div>

          <div className="mb-6 h-3 overflow-hidden rounded-full bg-white/5">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${pct}%` }}
              transition={{ duration: 1.1, ease: "easeOut" }}
              className="h-full bg-primary"
            />
          </div>

          <div className="space-y-4">
            {[
              { icon: <Timer className="h-4 w-4" />, label: "Pace", value: "127 steps/min" },
              { icon: <Mountain className="h-4 w-4" />, label: "Climb", value: "12 floors" },
              { icon: <Zap className="h-4 w-4" />, label: "Power", value: "High cadence" },
            ].map((item) => (
              <div
                key={item.label}
                className="flex items-center justify-between rounded-2xl border border-white/5 bg-white/3 px-5 py-4"
              >
                <div className="flex items-center gap-3 text-slate-400">
                  {item.icon}
                  <span className="text-sm font-bold">{item.label}</span>
                </div>
                <span className="text-sm font-bold text-white">{item.value}</span>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>

      <div className="grid grid-cols-1 gap-8 xl:grid-cols-[1.1fr_0.9fr]">
        <GlassCard>
          <div className="mb-6">
            <h2 className="font-headline text-2xl font-bold text-white">
              Weekly Steps Trend
            </h2>
            <p className="text-sm text-slate-400">
              Mock chart until you add tracking backend
            </p>
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stepsTrendData}>
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
                <Bar dataKey="steps" fill="#4edea3" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        <GlassCard>
          <div className="mb-6 text-[11px] font-black uppercase tracking-[0.24em] text-secondary">
            Sessions
          </div>

          <div className="space-y-4">
            {stepSessions.map((session) => (
              <div
                key={session.label}
                className="rounded-2xl border border-white/5 bg-white/3 px-5 py-4"
              >
                <div className="flex items-center justify-between">
                  <div className="text-sm font-bold text-white">{session.label}</div>
                  <div className="text-sm font-bold text-primary">
                    {session.value.toLocaleString()}
                  </div>
                </div>
                <div className="mt-2 text-[10px] font-black uppercase tracking-[0.18em] text-slate-500">
                  {session.duration}
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </motion.div>
  );
} 67