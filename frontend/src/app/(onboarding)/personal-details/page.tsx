"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { OnboardingShell } from "@/components/layout/onboarding-shell";
import { PersonalDetailsForm } from "@/features/onboarding/forms/personal-details-form";
import { getAccessToken } from "@/lib/auth/token-storage";

export default function PersonalDetailsPage() {
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

  return (
    <OnboardingShell progressStep={2} activeStepId="profile">
      <PersonalDetailsForm accessToken={accessToken} />
    </OnboardingShell>
  );
}