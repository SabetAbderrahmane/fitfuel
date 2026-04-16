"use client";

import type { ReactNode } from "react";
import { UserCircle } from "lucide-react";

import {
  OnboardingSideNav,
  type OnboardingStepId,
} from "@/features/onboarding/components/onboarding-side-nav";

export function OnboardingShell({
  children,
  progressStep,
  activeStepId,
}: Readonly<{
  children: ReactNode;
  progressStep: 1 | 2 | 3 | 4;
  activeStepId: OnboardingStepId;
}>) {
  return (
    <div className="min-h-screen bg-background text-on-surface font-sans selection:bg-primary/30">
      <nav className="fixed top-0 z-50 flex w-full items-center justify-between bg-[rgba(7,14,29,0.62)] px-6 py-4 shadow-2xl shadow-primary/5 backdrop-blur-3xl">
        <div className="font-headline text-2xl font-black tracking-tighter text-primary">
          FitFuel AI
        </div>

        <div className="flex items-center gap-4">
          <button
            type="button"
            aria-label="User profile"
            className="text-on-surface-variant transition-colors duration-200 hover:text-primary active:scale-95"
          >
            <UserCircle className="h-6 w-6" />
          </button>
        </div>
      </nav>

      <div className="flex pt-20">
        <OnboardingSideNav
          progressStep={progressStep}
          activeStepId={activeStepId}
        />

        <main className="relative flex-1 overflow-y-auto">
          <div className="pointer-events-none absolute inset-0 z-0 bg-[radial-gradient(circle_at_top_left,rgba(78,222,163,0.05),transparent_28%),linear-gradient(180deg,#07101f_0%,#071425_100%)]" />
          <div
            className="pointer-events-none absolute inset-0 z-0 opacity-[0.03]"
            style={{
              backgroundImage:
                "radial-gradient(#4edea3 0.6px, transparent 0.6px)",
              backgroundSize: "24px 24px",
            }}
          />

          <div className="relative z-10 flex min-h-[calc(100vh-80px)] w-full items-center justify-center px-6 py-10 md:px-10">
            <div className="flex w-full justify-center">
              {children}
            </div>
          </div>
        </main>
      </div>

      <div className="pointer-events-none fixed bottom-0 left-0 z-0 h-1/3 w-full bg-gradient-to-t from-background to-transparent opacity-50" />
    </div>
  );
}