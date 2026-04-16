"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchMyProfile } from "@/features/onboarding/api/profile";
import type { UserProfileResponse } from "@/features/onboarding/types/profile.types";

export function useProfileQuery(accessToken: string) {
  return useQuery<UserProfileResponse | null, Error>({
    queryKey: ["my-profile"],
    queryFn: async () => fetchMyProfile(accessToken),
    enabled: Boolean(accessToken),
    retry: 0,
    refetchOnWindowFocus: false,
  });
}