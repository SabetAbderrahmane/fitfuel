"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { OnboardingShell } from "@/components/layout/onboarding-shell";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { FinalPlanSummary } from "@/features/onboarding/components/final-plan-summary";
import { useFinalPlanQuery } from "@/features/onboarding/hooks/use-final-plan-query";
import { getAccessToken } from "@/lib/auth/token-storage";

export default function PlanPage() {
  const router = useRouter();
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setAccessToken(getAccessToken());
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated) {
      return;
    }

    if (!accessToken) {
      router.replace("/login");
    }
  }, [accessToken, hydrated, router]);

  const finalPlanQuery = useFinalPlanQuery(accessToken);

  useEffect(() => {
    if (!hydrated || finalPlanQuery.isLoading) {
      return;
    }

    if (finalPlanQuery.data === null) {
      router.replace("/goals");
    }
  }, [finalPlanQuery.data, finalPlanQuery.isLoading, hydrated, router]);

  if (!hydrated) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background">
        <LoadingState label="Preparing your final plan..." className="text-primary" />
      </main>
    );
  }

  if (!accessToken) {
    return null;
  }

  return (
    <OnboardingShell progressStep={4} activeStepId="finish">
      {finalPlanQuery.isLoading ? (
        <div className="w-full max-w-5xl rounded-[2rem] bg-[rgba(46,53,69,0.35)] p-10 backdrop-blur-2xl">
          <LoadingState label="Loading your final plan..." className="text-primary" />
        </div>
      ) : finalPlanQuery.isError ? (
        <div className="w-full max-w-5xl rounded-[2rem] bg-[rgba(46,53,69,0.35)] p-10 backdrop-blur-2xl">
          <ErrorState message={finalPlanQuery.error.message} />
        </div>
      ) : finalPlanQuery.data ? (
        <FinalPlanSummary summary={finalPlanQuery.data} />
      ) : null}
    </OnboardingShell>
  );
}