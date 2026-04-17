"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import {
  Camera,
  ChevronRight,
  ClipboardList,
  Plus,
  Scale,
  Utensils,
  X,
  type LucideIcon,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import type {
  FoodLogResponse,
  PhotoUploadResponse,
  WeightLogResponse,
} from "@/features/dashboard/types/dashboard.types";

type ActivityItem = {
  id: string;
  icon: LucideIcon;
  title: string;
  meta: string;
  color: string;
  createdAt: string;
};

function formatRelativeTime(dateValue: string): string {
  const now = Date.now();
  const value = new Date(dateValue).getTime();
  const diffMs = Math.max(now - value, 0);

  const minute = 60_000;
  const hour = 60 * minute;
  const day = 24 * hour;

  if (diffMs < hour) {
    const minutes = Math.max(1, Math.round(diffMs / minute));
    return `${minutes}m ago`;
  }

  if (diffMs < day) {
    const hours = Math.max(1, Math.round(diffMs / hour));
    return `${hours}h ago`;
  }

  const days = Math.max(1, Math.round(diffMs / day));
  return `${days}d ago`;
}

function ActivityRow({
  icon: Icon,
  title,
  meta,
  color,
  index,
}: Readonly<{
  icon: LucideIcon;
  title: string;
  meta: string;
  color: string;
  index: number;
}>) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.8 + index * 0.1, duration: 0.5 }}
      whileHover={{ x: 5 }}
      className="group flex cursor-default items-center justify-between rounded-xl p-3 transition-colors hover:bg-surface-high/50"
    >
      <div className="flex items-center gap-4">
        <div
          className="relative flex h-10 w-10 items-center justify-center overflow-hidden rounded-full bg-surface-high"
          style={{ color }}
        >
          <motion.div
            className="absolute inset-0 opacity-10"
            style={{ backgroundColor: color }}
            animate={{ opacity: [0.1, 0.2, 0.1] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
          <Icon className="relative z-10 h-5 w-5" />
        </div>

        <div>
          <h4 className="text-sm font-bold tracking-tight text-heading">
            {title}
          </h4>
          <p className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
            {meta}
          </p>
        </div>
      </div>

      <ChevronRight className="h-4 w-4 text-muted-foreground transition-colors group-hover:text-heading" />
    </motion.div>
  );
}

function LogFoodChooser({
  open,
  onClose,
  onManual,
  onPhoto,
}: Readonly<{
  open: boolean;
  onClose: () => void;
  onManual: () => void;
  onPhoto: () => void;
}>) {
  return (
    <AnimatePresence>
      {open ? (
        <>
          <motion.button
            type="button"
            aria-label="Close log food chooser"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-[90] bg-black/55 backdrop-blur-sm"
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.94, y: 18 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: 12 }}
            transition={{ duration: 0.22, ease: "easeOut" }}
            className="fixed inset-0 z-[100] flex items-center justify-center px-4"
          >
            <div className="dashboard-kinetic-card relative w-full max-w-md rounded-[1.75rem] p-6">
              <button
                type="button"
                onClick={onClose}
                aria-label="Close"
                className="absolute right-4 top-4 flex h-9 w-9 items-center justify-center rounded-full bg-surface-high text-muted-foreground transition-colors hover:text-heading"
              >
                <X className="h-4 w-4" />
              </button>

              <div className="mb-6 pr-10">
                <p className="text-[10px] font-black uppercase tracking-[0.22em] text-primary">
                  Log Food
                </p>
                <h3 className="mt-2 font-display text-2xl font-black tracking-tight text-heading">
                  Choose how you want to log it
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                  You can log food manually by typing it, or use a photo and let
                  the AI estimate it first.
                </p>
              </div>

              <div className="space-y-3">
                <motion.button
                  whileHover={{ y: -2, scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                  type="button"
                  onClick={onManual}
                  className="flex w-full items-center gap-4 rounded-2xl border border-white/5 bg-surface-high px-5 py-4 text-left transition-colors hover:border-primary/20 hover:bg-surface-low"
                >
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
                    <ClipboardList className="h-5 w-5" />
                  </div>

                  <div className="flex-1">
                    <div className="text-sm font-black tracking-tight text-heading">
                      Type it manually
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Search foods and enter quantities yourself.
                    </div>
                  </div>

                  <ChevronRight className="h-4 w-4 text-muted-foreground" />
                </motion.button>

                <motion.button
                  whileHover={{ y: -2, scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                  type="button"
                  onClick={onPhoto}
                  className="flex w-full items-center gap-4 rounded-2xl border border-primary/15 bg-primary/10 px-5 py-4 text-left transition-colors hover:bg-primary/15"
                >
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    <Camera className="h-5 w-5" />
                  </div>

                  <div className="flex-1">
                    <div className="text-sm font-black tracking-tight text-heading">
                      Use a photo
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Upload a meal photo and run AI calorie estimation.
                    </div>
                  </div>

                  <ChevronRight className="h-4 w-4 text-primary" />
                </motion.button>
              </div>
            </div>
          </motion.div>
        </>
      ) : null}
    </AnimatePresence>
  );
}

type DashboardRecentActivityProps = {
  foodLogs: FoodLogResponse[];
  weightLogs: WeightLogResponse[];
  photoUploads: PhotoUploadResponse[];
};

export function DashboardRecentActivity({
  foodLogs,
  weightLogs,
  photoUploads,
}: Readonly<DashboardRecentActivityProps>) {
  const router = useRouter();
  const [chooserOpen, setChooserOpen] = useState(false);

  const recentItems = useMemo<ActivityItem[]>(() => {
    const foodItems: ActivityItem[] = foodLogs.map((log) => ({
      id: `food-${log.id}`,
      icon: Utensils,
      title: log.items[0]?.food_name_snapshot ?? "Food log entry",
      meta: `${Math.round(log.total_calories)} kcal • ${formatRelativeTime(log.created_at)}`,
      color: "#4EDEA3",
      createdAt: log.created_at,
    }));

    const weightItems: ActivityItem[] = weightLogs.map((log) => ({
      id: `weight-${log.id}`,
      icon: Scale,
      title: "Weight check-in",
      meta: `${log.weight_kg.toFixed(1)} kg • ${formatRelativeTime(log.created_at)}`,
      color: "#ADC6FF",
      createdAt: log.created_at,
    }));

    const photoItems: ActivityItem[] = photoUploads.map((upload) => ({
      id: `photo-${upload.id}`,
      icon: Camera,
      title:
        upload.predictions[0]?.predicted_label ??
        upload.original_filename ??
        "Photo uploaded",
      meta: `AI photo • ${formatRelativeTime(upload.created_at)}`,
      color: "#FFB95F",
      createdAt: upload.created_at,
    }));

    return [...foodItems, ...weightItems, ...photoItems]
      .sort(
        (first, second) =>
          new Date(second.createdAt).getTime() -
          new Date(first.createdAt).getTime()
      )
      .slice(0, 3);
  }, [foodLogs, photoUploads, weightLogs]);

  const goToManualLog = () => {
    setChooserOpen(false);
    router.push("/food-log");
  };

  const goToPhotoEstimator = () => {
    setChooserOpen(false);
    router.push("/photo-estimator");
  };

  return (
    <>
      <motion.div
        whileHover={{ y: -5, rotateX: 2, rotateY: -1 }}
        style={{ perspective: 1000 }}
        className="dashboard-kinetic-card group flex h-full flex-col rounded-2xl p-8"
      >
        <div className="pointer-events-none absolute inset-0 bg-white/[0.01]" />

        <div className="relative z-10 mb-6 flex items-center justify-between">
          <h3 className="font-display text-lg font-black text-heading">
            Recent Activity
          </h3>

          <div className="flex gap-2">
            <motion.button
              whileHover={{ scale: 1.1, rotate: 15 }}
              whileTap={{ scale: 0.9 }}
              type="button"
              onClick={() => setChooserOpen(true)}
              className="flex h-8 w-8 items-center justify-center rounded-full bg-surface-high transition-colors hover:bg-muted"
            >
              <Camera className="h-4 w-4 text-muted-foreground" />
            </motion.button>
          </div>
        </div>

        <div className="relative z-10 flex-1 space-y-4">
          {recentItems.length > 0 ? (
            recentItems.map((item, index) => (
              <ActivityRow
                key={item.id}
                icon={item.icon}
                title={item.title}
                meta={item.meta}
                color={item.color}
                index={index}
              />
            ))
          ) : (
            <p className="text-sm font-medium text-muted-foreground">
              No recent dashboard activity yet.
            </p>
          )}
        </div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="mt-8"
        >
          <Button
            type="button"
            onClick={() => setChooserOpen(true)}
            className="dashboard-glow-green dashboard-pulse-primary relative flex w-full items-center justify-center gap-2 overflow-hidden rounded-2xl bg-primary px-6 py-6 font-black text-primary-foreground shadow-xl shadow-primary/20 transition-all hover:shadow-primary/40"
          >
            <motion.div className="absolute inset-0 translate-x-[-100%] bg-white/20 transition-transform duration-700 ease-in-out group-hover:translate-x-[100%]" />
            <span className="relative z-10">Log Food</span>
            <Plus className="relative z-10 h-5 w-5" />
          </Button>
        </motion.div>
      </motion.div>

      <LogFoodChooser
        open={chooserOpen}
        onClose={() => setChooserOpen(false)}
        onManual={goToManualLog}
        onPhoto={goToPhotoEstimator}
      />
    </>
  );
}