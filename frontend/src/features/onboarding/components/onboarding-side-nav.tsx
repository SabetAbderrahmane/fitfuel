"use client";

import { motion } from "framer-motion";
import { User, Hexagon, Dumbbell, CheckCircle2 } from "lucide-react";

import { cn } from "@/lib/utils/cn";

export type OnboardingStepId = "profile" | "goals" | "activity" | "finish";

const steps = [
  { id: "profile", label: "PROFILE", icon: User },
  { id: "goals", label: "GOALS", icon: Hexagon },
  { id: "activity", label: "ACTIVITY", icon: Dumbbell },
  { id: "finish", label: "FINISH", icon: CheckCircle2 },
] as const;

export function OnboardingSideNav({
  progressStep,
  activeStepId,
}: Readonly<{
  progressStep: 1 | 2 | 3 | 4;
  activeStepId: OnboardingStepId;
}>) {
  return (
    <aside className="mt-4 hidden h-[calc(100vh-80px)] w-64 flex-col bg-transparent p-6 md:flex">
      <div className="mb-12 px-4">
        <div className="mb-2 font-headline text-3xl font-black tracking-tighter text-primary">
          Onboarding
        </div>
        <div className="text-[10px] font-black uppercase tracking-[0.2em] text-on-surface-variant/40">
          Step {progressStep} of 4
        </div>
      </div>

      <nav className="space-y-6">
        {steps.map((step, index) => {
          const isActive = step.id === activeStepId;
          const Icon = step.icon;

          return (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className={cn(
                "cursor-default rounded-full px-6 py-4 font-headline text-[11px] font-black tracking-[0.1em] transition-all duration-300",
                "flex items-center gap-4",
                isActive
                  ? "bg-primary/10 text-primary shadow-[0_10px_30px_rgba(78,222,163,0.1)]"
                  : "text-on-surface-variant/40 hover:bg-white/5 hover:text-on-surface"
              )}
            >
              <Icon
                className={cn(
                  "h-5 w-5",
                  isActive ? "text-primary" : "text-on-surface-variant/40"
                )}
              />
              <span>{step.label}</span>
            </motion.div>
          );
        })}
      </nav>
    </aside>
  );
}