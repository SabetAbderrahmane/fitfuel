"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { WelcomeStepOne } from "@/features/onboarding/components/welcome-step-one";
import { useOnboardingStatusQuery } from "@/features/onboarding/hooks/use-onboarding-status-query";
import { getAccessToken } from "@/lib/auth/token-storage";

export default function WelcomePage() {
  const router = useRouter();
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setAccessToken(getAccessToken());
    setHydrated(true);
  }, []);

  const onboardingStatusQuery = useOnboardingStatusQuery(accessToken);

  useEffect(() => {
    if (!hydrated) {
      return;
    }

    if (!accessToken) {
      router.replace("/login");
    }
  }, [accessToken, hydrated, router]);

  useEffect(() => {
    if (onboardingStatusQuery.data?.isComplete) {
      router.replace("/dashboard");
    }
  }, [onboardingStatusQuery.data?.isComplete, router]);

  if (!hydrated) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background">
        <LoadingState label="Preparing your onboarding..." className="text-primary" />
      </main>
    );
  }

  if (!accessToken) {
    return null;
  }

  if (onboardingStatusQuery.isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background">
        <LoadingState label="Checking your setup..." className="text-primary" />
      </main>
    );
  }

  if (onboardingStatusQuery.isError) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background px-6">
        <ErrorState message={onboardingStatusQuery.error.message} />
      </main>
    );
  }

  if (onboardingStatusQuery.data?.isComplete) {
    return null;
  }

  return <WelcomeStepOne />;
}