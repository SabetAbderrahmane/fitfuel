"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchOnboardingStatus } from "@/features/onboarding/api/onboarding-status";
import type { OnboardingStatus } from "@/features/onboarding/types/onboarding.types";

export function useOnboardingStatusQuery(accessToken: string | null) {
  return useQuery<OnboardingStatus, Error>({
    queryKey: ["onboarding-status", accessToken],
    queryFn: async () => fetchOnboardingStatus(accessToken as string),
    enabled: Boolean(accessToken),
    retry: 0,
    refetchOnWindowFocus: false,
  });
}