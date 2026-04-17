"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchDashboardData } from "@/features/dashboard/api/dashboard";
import type { DashboardData } from "@/features/dashboard/types/dashboard.types";

export function useDashboardQuery(accessToken: string | null) {
  return useQuery<DashboardData, Error>({
    queryKey: ["dashboard-data", accessToken],
    queryFn: async () => fetchDashboardData(accessToken as string),
    enabled: Boolean(accessToken),
    retry: 0,
    refetchOnWindowFocus: false,
  });
}