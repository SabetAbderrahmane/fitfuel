"use client";

import { motion } from "framer-motion";
import {
  LineChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
} from "recharts";

import type { WeightLogResponse } from "@/features/dashboard/types/dashboard.types";

function formatDayLabel(dateValue: string): string {
  return new Date(dateValue)
    .toLocaleDateString("en-US", { weekday: "short" })
    .toUpperCase();
}

type DashboardWeightTrendProps = {
  weightLogs: WeightLogResponse[];
};

export function DashboardWeightTrend({
  weightLogs,
}: Readonly<DashboardWeightTrendProps>) {
  const sortedLogs = [...weightLogs].sort(
    (first, second) =>
      new Date(first.logged_for_date).getTime() -
      new Date(second.logged_for_date).getTime()
  );

  const chartData = sortedLogs.map((log) => ({
    day: formatDayLabel(log.logged_for_date),
    weight: log.weight_kg,
  }));

  const weightDelta =
    sortedLogs.length >= 2
      ? sortedLogs[sortedLogs.length - 1].weight_kg - sortedLogs[0].weight_kg
      : 0;

  const deltaText =
    sortedLogs.length >= 2
      ? `${weightDelta > 0 ? "+" : ""}${weightDelta.toFixed(1)} kg`
      : "0.0 kg";

  if (sortedLogs.length === 0) {
    return (
      <motion.div
        whileHover={{ y: -5, rotateX: 1, rotateY: -1 }}
        style={{ perspective: 1000 }}
        className="dashboard-kinetic-card h-full space-y-6 rounded-2xl p-8"
      >
        <div className="flex items-center justify-between">
          <h3 className="font-display text-lg font-bold text-heading">
            Weight Trend
          </h3>
          <span className="text-sm font-bold text-muted-foreground">
            No logs yet
          </span>
        </div>

        <p className="text-sm font-medium text-muted-foreground">
          Add weight logs to see your seven-day trend here.
        </p>
      </motion.div>
    );
  }

  return (
    <motion.div
      whileHover={{ y: -5, rotateX: 1, rotateY: -1 }}
      style={{ perspective: 1000 }}
      className="dashboard-kinetic-card h-full space-y-6 rounded-2xl p-8"
    >
      <div className="flex items-center justify-between">
        <h3 className="font-display text-lg font-bold text-heading">
          Weight Trend
        </h3>
        <span className="text-sm font-bold text-primary">
          {deltaText}
          <span className="ml-1 font-normal uppercase text-muted-foreground">
            Last 7 Days
          </span>
        </span>
      </div>

      <div className="h-[200px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <XAxis
              dataKey="day"
              axisLine={false}
              tickLine={false}
              tick={{
                fill: "#BBCABF",
                fontSize: 10,
                fontWeight: 600,
              }}
              dy={10}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#232A3A",
                border: "none",
                borderRadius: "12px",
                color: "#FFFFFF",
              }}
              itemStyle={{ color: "#4EDEA3" }}
              cursor={{ stroke: "#232A3A", strokeWidth: 2 }}
            />
            <Line
              type="monotone"
              dataKey="weight"
              stroke="#4EDEA3"
              strokeWidth={4}
              dot={{
                fill: "#4EDEA3",
                strokeWidth: 2,
                r: 6,
                stroke: "#0C1322",
              }}
              activeDot={{
                r: 8,
                stroke: "#4EDEA3",
                strokeWidth: 2,
                fill: "#0C1322",
              }}
              animationDuration={2000}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}