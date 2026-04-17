"use client";

import { motion, type Variants } from "framer-motion";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  Activity,
  ArrowRight,
  Minus,
  Sparkles,
  TrendingDown,
  TrendingUp,
} from "lucide-react";

import {
  calorieTrendData,
  macroRatioData,
  recentMetrics,
  weightTrendData,
} from "@/features/progress/data/progress.mock";

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.15,
    },
  },
};

const itemVariants: Variants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      duration: 0.55,
      ease: [0.25, 0.1, 0.25, 1],
    },
  },
};

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

function MiniStatCard({
  title,
  value,
  subtitle,
  tone = "primary",
}: Readonly<{
  title: string;
  value: string;
  subtitle: string;
  tone?: "primary" | "secondary" | "tertiary";
}>) {
  const toneClass =
    tone === "primary"
      ? "text-primary"
      : tone === "secondary"
      ? "text-secondary"
      : "text-[#90a8ff]";

  return (
    <GlassCard className="h-full">
      <div className={`text-[11px] font-black uppercase tracking-[0.24em] ${toneClass}`}>
        {title}
      </div>
      <div className="mt-4 font-headline text-4xl font-black text-white">
        {value}
      </div>
      <p className="mt-3 text-sm text-slate-400">{subtitle}</p>
    </GlassCard>
  );
}

function HeroSection() {
  return (
    <GlassCard className="relative overflow-hidden lg:col-span-2">
      <div className="pointer-events-none absolute right-0 top-0 h-full w-1/2 opacity-20">
        <div className="h-full w-full bg-gradient-to-l from-primary to-transparent" />
      </div>

      <div className="relative">
        <h1 className="font-headline text-4xl font-extrabold tracking-tight text-white md:text-5xl">
          Peak Analytics.
        </h1>
        <p className="mt-4 max-w-xl text-lg leading-relaxed text-slate-400">
          Your biometrics indicate strong metabolic efficiency. Keep this momentum
          for 4 more days to reach “Elite” status.
        </p>
      </div>

      <div className="mt-8 flex flex-wrap gap-4">
        <motion.button
          whileHover={{ scale: 1.04, y: -2 }}
          whileTap={{ scale: 0.96 }}
          className="rounded-full bg-primary px-8 py-3 font-black text-[#003824] shadow-[0_8px_20px_-4px_rgba(78,222,163,0.4)]"
        >
          Download Report
        </motion.button>

        <button className="rounded-full px-8 py-3 font-bold text-primary transition-colors hover:bg-primary/10">
          Compare Period
        </button>
      </div>
    </GlassCard>
  );
}

function AdherenceScore() {
  const percentage = 87;
  const circumference = 2 * Math.PI * 88;
  const strokeDashoffset = circumference - (circumference * percentage) / 100;

  return (
    <GlassCard className="flex h-full flex-col items-center justify-center text-center">
      <h3 className="mb-6 font-headline text-lg font-bold text-slate-400">
        Adherence Score
      </h3>

      <div className="relative flex h-48 w-48 items-center justify-center">
        <svg className="h-full w-full -rotate-90">
          <circle
            className="text-white/10"
            cx="96"
            cy="96"
            fill="transparent"
            r="88"
            stroke="currentColor"
            strokeWidth="12"
          />
          <motion.circle
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.4, delay: 0.35, ease: "easeOut" }}
            className="text-primary"
            cx="96"
            cy="96"
            fill="transparent"
            r="88"
            stroke="currentColor"
            strokeDasharray={circumference}
            strokeWidth="12"
            strokeLinecap="round"
          />
        </svg>

        <div className="absolute flex flex-col items-center">
          <span className="font-headline text-5xl font-black text-white">
            {percentage}%
          </span>
          <span className="mt-1 text-xs font-black uppercase tracking-[0.22em] text-primary">
            Excellent
          </span>
        </div>
      </div>

      <p className="mt-6 text-sm text-slate-400">+12% from last week</p>
    </GlassCard>
  );
}

function WeightTrendCard() {
  return (
    <GlassCard className="lg:col-span-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h2 className="font-headline text-2xl font-bold text-white">Weight Trend</h2>
          <p className="text-sm font-medium text-slate-400">
            Progress toward 82kg target
          </p>
        </div>

        <div className="flex rounded-full bg-white/5 p-1">
          <button className="rounded-full bg-[#0c1322] px-4 py-1 text-xs font-bold text-white shadow-sm">
            30 Days
          </button>
          <button className="px-4 py-1 text-xs font-bold text-slate-400">
            90 Days
          </button>
        </div>
      </div>

      <div className="h-[260px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={weightTrendData}>
            <Tooltip
              cursor={{ fill: "rgba(78,222,163,0.08)" }}
              contentStyle={{
                background: "#141b2b",
                border: "1px solid rgba(255,255,255,0.08)",
                borderRadius: "12px",
                color: "#dce2f7",
                fontSize: 12,
              }}
            />
            <ReferenceLine
              y={82.5}
              stroke="#4edea3"
              strokeDasharray="4 4"
              strokeOpacity={0.35}
            />
            <Bar dataKey="value" fill="#4edea3" opacity={0.5} radius={[3, 3, 0, 0]} />
            <XAxis hide dataKey="label" />
            <YAxis hide domain={["dataMin - 1", "dataMax + 1"]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-6 flex justify-between border-t border-white/5 pt-4 text-[10px] font-black uppercase tracking-[0.24em] text-slate-500">
        <span>Oct 01</span>
        <span>Oct 15</span>
        <span>Today</span>
      </div>
    </GlassCard>
  );
}

function AIInsightCard() {
  return (
    <GlassCard className="relative overflow-hidden lg:col-span-4">
      <motion.div
        animate={{ x: [0, 50, 0], y: [0, 30, 0] }}
        transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        className="pointer-events-none absolute -right-20 -top-20 h-64 w-64 rounded-full bg-primary/20 blur-[80px]"
      />

      <div className="mb-6 flex items-center justify-between">
        <span className="flex items-center gap-2 rounded-full border border-primary/20 bg-primary/20 px-3 py-1 text-xs font-black uppercase tracking-[0.22em] text-primary">
          <Sparkles className="h-3 w-3 fill-current" />
          Smart Insight
        </span>
      </div>

      <h3 className="font-headline text-2xl font-bold text-white">
        Weekly Performance Insight
      </h3>

      <p className="mt-4 text-lg font-medium italic leading-relaxed text-white/90">
        Your protein intake has been{" "}
        <span className="font-bold text-primary">exceptionally consistent</span>.
        This directly contributed to your 1.2% body fat reduction this week. Consider
        increasing water intake by 500ml on training days to optimize recovery.
      </p>

      <motion.button
        whileHover={{ x: 4 }}
        className="mt-8 flex items-center gap-2 font-bold text-primary"
      >
        Explore Details
        <ArrowRight className="h-4 w-4" />
      </motion.button>
    </GlassCard>
  );
}

function CalorieBalanceCard() {
  return (
    <GlassCard className="lg:col-span-4">
      <div className="mb-6">
        <div className="text-[11px] font-black uppercase tracking-[0.24em] text-primary">
          Daily Calories
        </div>
        <h3 className="mt-2 font-headline text-2xl font-bold text-white">
          Energy Balance
        </h3>
      </div>

      <div className="mb-5 flex items-end gap-3">
        <span className="font-headline text-5xl font-black text-white">2,420</span>
        <span className="pb-2 text-sm font-black uppercase tracking-[0.18em] text-slate-500">
          kcal
        </span>
      </div>

      <div className="mb-6 h-3 overflow-hidden rounded-full bg-white/5">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: "82%" }}
          transition={{ duration: 1.1, ease: "easeOut" }}
          className="h-full bg-primary"
        />
      </div>

      <div className="h-[180px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={calorieTrendData}>
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
                fontSize: 12,
              }}
            />
            <Bar dataKey="target" fill="#2e3545" radius={[5, 5, 0, 0]} />
            <Bar dataKey="actual" fill="#4edea3" radius={[5, 5, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </GlassCard>
  );
}

function MacroRatiosCard() {
  return (
    <GlassCard className="lg:col-span-4">
      <div className="mb-6">
        <div className="text-[11px] font-black uppercase tracking-[0.24em] text-secondary">
          Macro Ratios
        </div>
        <h3 className="mt-2 font-headline text-2xl font-bold text-white">
          Fuel Distribution
        </h3>
      </div>

      <div className="mx-auto h-[220px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={macroRatioData}
              dataKey="current"
              nameKey="label"
              innerRadius={65}
              outerRadius={90}
              paddingAngle={6}
              stroke="transparent"
            >
              {macroRatioData.map((entry) => (
                <Cell key={entry.label} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                background: "#141b2b",
                border: "1px solid rgba(255,255,255,0.08)",
                borderRadius: "12px",
                color: "#dce2f7",
                fontSize: 12,
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="space-y-3">
        {macroRatioData.map((entry) => {
          const pct = Math.min((entry.current / entry.target) * 100, 100);

          return (
            <div key={entry.label}>
              <div className="mb-1 flex items-center justify-between text-sm">
                <span className="font-bold text-white">{entry.label}</span>
                <span className="text-slate-400">
                  {entry.current} / {entry.target}g
                </span>
              </div>

              <div className="h-2 overflow-hidden rounded-full bg-white/5">
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${pct}%`,
                    backgroundColor: entry.color,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </GlassCard>
  );
}

function RecentMetricsCard() {
  return (
    <GlassCard className="lg:col-span-12">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h3 className="font-headline text-2xl font-bold text-white">
            Recent Metrics
          </h3>
          <p className="text-sm text-slate-400">
            Latest weigh-ins and body composition updates
          </p>
        </div>

        <span className="flex items-center gap-2 rounded-full bg-white/5 px-4 py-2 text-xs font-black uppercase tracking-[0.2em] text-primary">
          <Activity className="h-4 w-4" />
          Live Feed
        </span>
      </div>

      <div className="overflow-hidden rounded-2xl border border-white/5">
        <table className="w-full border-collapse">
          <thead className="bg-white/[0.03]">
            <tr className="text-left text-[11px] uppercase tracking-[0.22em] text-slate-500">
              <th className="px-6 py-4">Date</th>
              <th className="px-6 py-4">Weight</th>
              <th className="px-6 py-4">Body Fat</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4 text-right">Trend</th>
            </tr>
          </thead>

          <tbody>
            {recentMetrics.map((metric) => (
              <tr
                key={metric.date}
                className="border-t border-white/5 transition-colors hover:bg-white/[0.03]"
              >
                <td className="px-6 py-5 text-sm font-bold text-slate-400">
                  {metric.date}
                </td>
                <td className="px-6 py-5 font-headline font-bold text-white">
                  {metric.weight}kg
                </td>
                <td className="px-6 py-5 font-headline font-bold text-white">
                  {metric.bodyFat}%
                </td>
                <td className="px-6 py-5">
                  <span
                    className={`rounded-full px-3 py-1 text-[10px] font-black uppercase tracking-[0.18em] ${
                      metric.status === "Increase"
                        ? "bg-secondary/20 text-secondary"
                        : metric.status === "Stable"
                        ? "bg-white/10 text-slate-300"
                        : "bg-primary/20 text-primary"
                    }`}
                  >
                    {metric.status}
                  </span>
                </td>
                <td className="px-6 py-5 text-right">
                  {metric.trend === "down" ? (
                    <TrendingDown className="ml-auto h-5 w-5 text-primary" />
                  ) : metric.trend === "up" ? (
                    <TrendingUp className="ml-auto h-5 w-5 text-secondary" />
                  ) : (
                    <Minus className="ml-auto h-5 w-5 text-slate-400" />
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </GlassCard>
  );
}

export function DailyCaloriesPage() {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-10"
    >
      <motion.section
        variants={itemVariants}
        className="grid grid-cols-1 gap-8 lg:grid-cols-3"
      >
        <HeroSection />
        <AdherenceScore />
      </motion.section>

      <motion.section
        variants={itemVariants}
        className="grid grid-cols-1 gap-8 lg:grid-cols-12"
      >
        <WeightTrendCard />
        <AIInsightCard />
        <CalorieBalanceCard />
        <MacroRatiosCard />

        <div className="grid grid-cols-1 gap-8 md:grid-cols-3 lg:col-span-4">
          <MiniStatCard
            title="Weight Goal"
            value="84.2kg"
            subtitle="1.7kg remaining to target"
          />
          <MiniStatCard
            title="Consistency"
            value="11 Days"
            subtitle="Tracking streak is still alive"
            tone="secondary"
          />
          <MiniStatCard
            title="Power Session"
            value="92%"
            subtitle="Workout fueling quality"
            tone="tertiary"
          />
        </div>

        <RecentMetricsCard />
      </motion.section>
    </motion.div>
  );
}