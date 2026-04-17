"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, type Variants } from "framer-motion";

import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { DashboardCalorieHero } from "@/features/dashboard/components/dashboard-calorie-hero";
import { DashboardMacroBreakdown } from "@/features/dashboard/components/dashboard-macro-breakdown";
import { DashboardMealPlan } from "@/features/dashboard/components/dashboard-meal-plan";
import { DashboardRecentActivity } from "@/features/dashboard/components/dashboard-recent-activity";
import { DashboardWeightTrend } from "@/features/dashboard/components/dashboard-weight-trend";
import { useDashboardQuery } from "@/features/dashboard/hooks/use-dashboard-query";
import { getAccessToken } from "@/lib/auth/token-storage";

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.2,
    },
  },
};

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 30, filter: "blur(10px)" },
  visible: {
    opacity: 1,
    y: 0,
    filter: "blur(0px)",
    transition: {
      type: "spring",
      stiffness: 70,
      damping: 20,
    },
  },
};

export default function DashboardPage() {
  const router = useRouter();
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setAccessToken(getAccessToken());
    setHydrated(true);
  }, []);

  const dashboardQuery = useDashboardQuery(accessToken);

  useEffect(() => {
    if (!hydrated) {
      return;
    }

    if (!accessToken) {
      router.replace("/login");
    }
  }, [accessToken, hydrated, router]);

  useEffect(() => {
    if (!dashboardQuery.data) {
      return;
    }

    if (!dashboardQuery.data.profile || !dashboardQuery.data.currentGoal) {
      router.replace("/welcome");
    }
  }, [dashboardQuery.data, router]);

  const derivedData = useMemo(() => {
    if (!dashboardQuery.data?.currentGoal) {
      return null;
    }

    const snapshot = dashboardQuery.data.latestSnapshot;
    const currentGoal = dashboardQuery.data.currentGoal;

    return {
      consumedCalories: Math.round(snapshot?.consumed_calories ?? 0),
      targetCalories: snapshot?.target_calories ?? currentGoal.target_calories,
      protein: {
        current: Math.round(snapshot?.consumed_protein_g ?? 0),
        target: snapshot?.target_protein_g ?? currentGoal.target_protein_g,
      },
      carbs: {
        current: Math.round(snapshot?.consumed_carbs_g ?? 0),
        target: snapshot?.target_carbs_g ?? currentGoal.target_carbs_g,
      },
      fats: {
        current: Math.round(snapshot?.consumed_fat_g ?? 0),
        target: snapshot?.target_fat_g ?? currentGoal.target_fat_g,
      },
    };
  }, [dashboardQuery.data]);

  if (!hydrated) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background">
        <LoadingState label="Preparing your dashboard..." className="text-primary" />
      </main>
    );
  }

  if (!accessToken) {
    return null;
  }

  if (dashboardQuery.isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background">
        <LoadingState label="Loading your dashboard..." className="text-primary" />
      </main>
    );
  }

  if (dashboardQuery.isError) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background px-6">
        <ErrorState message={dashboardQuery.error.message} />
      </main>
    );
  }

  if (
    !dashboardQuery.data ||
    !dashboardQuery.data.profile ||
    !dashboardQuery.data.currentGoal ||
    !derivedData
  ) {
    return null;
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-background pb-12">
      <div className="dashboard-grain" />
      <div className="dashboard-scanline" />

      <main
        className="relative z-10 mx-auto max-w-7xl space-y-10 px-6"
        style={{ perspective: 2000 }}
      >
        <motion.div
          className="grid grid-cols-1 gap-8 lg:grid-cols-3"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.div className="lg:col-span-2" variants={itemVariants}>
            <DashboardCalorieHero
              consumedCalories={derivedData.consumedCalories}
              targetCalories={derivedData.targetCalories}
            />
          </motion.div>

          <motion.div variants={itemVariants}>
            <DashboardMacroBreakdown
              protein={derivedData.protein}
              carbs={derivedData.carbs}
              fats={derivedData.fats}
            />
          </motion.div>

          <motion.div className="lg:col-span-3" variants={itemVariants}>
            <DashboardMealPlan mealPlan={dashboardQuery.data.latestMealPlan} />
          </motion.div>

          <motion.div className="lg:col-span-2" variants={itemVariants}>
            <DashboardWeightTrend weightLogs={dashboardQuery.data.weightLogs} />
          </motion.div>

          <motion.div variants={itemVariants}>
            <DashboardRecentActivity
              foodLogs={dashboardQuery.data.foodLogs}
              weightLogs={dashboardQuery.data.weightLogs}
              photoUploads={dashboardQuery.data.photoUploads}
            />
          </motion.div>
        </motion.div>
      </main>

      <style jsx global>{`
        .dashboard-grain {
          position: fixed;
          inset: 0;
          width: 100%;
          height: 100%;
          opacity: 0.04;
          pointer-events: none;
          z-index: 40;
          background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
        }

        .dashboard-glass {
          background: rgba(46, 53, 69, 0.4);
          backdrop-filter: blur(24px) saturate(180%);
          -webkit-backdrop-filter: blur(24px) saturate(180%);
          border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        }

        .dashboard-kinetic-card {
          background: #141b2b;
          border: 1px solid rgba(255, 255, 255, 0.05);
          box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.6);
          transition: all 0.5s ease;
          position: relative;
          overflow: hidden;
        }

        .dashboard-kinetic-card::after {
          content: "";
          position: absolute;
          inset: 0;
          background: linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.05) 0%,
            transparent 40%,
            transparent 60%,
            rgba(255, 255, 255, 0.02) 100%
          );
          pointer-events: none;
        }

        .dashboard-kinetic-card:hover {
          border-color: rgba(255, 255, 255, 0.1);
          box-shadow: 0 0 50px -10px rgba(78, 222, 163, 0.08);
        }

        .dashboard-glow-green {
          filter: drop-shadow(0 0 8px rgba(78, 222, 163, 0.3));
        }

        .dashboard-progress-ring {
          transform: rotate(-90deg);
        }

        @keyframes dashboard-scanline {
          0% {
            transform: translateY(-100%);
            opacity: 0;
          }
          50% {
            opacity: 0.5;
          }
          100% {
            transform: translateY(1000%);
            opacity: 0;
          }
        }

        .dashboard-scanline {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 2px;
          background: linear-gradient(
            to right,
            transparent,
            rgba(78, 222, 163, 0.2),
            transparent
          );
          animation: dashboard-scanline 8s linear infinite;
          pointer-events: none;
          z-index: 20;
        }

        @keyframes dashboard-pulse-soft {
          0%,
          100% {
            opacity: 1;
            transform: scale(1);
          }
          50% {
            opacity: 0.8;
            transform: scale(1.02);
          }
        }

        .dashboard-pulse-primary {
          animation: dashboard-pulse-soft 3s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}