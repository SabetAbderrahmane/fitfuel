"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchAssistantPageData } from "@/features/assistant/api/assistant";
import type { AssistantPageData } from "@/features/assistant/types/assistant.types";

export function useAssistantPageQuery(accessToken: string | null) {
  return useQuery<AssistantPageData, Error>({
    queryKey: ["assistant-page", accessToken],
    queryFn: async () => fetchAssistantPageData(accessToken as string),
    enabled: Boolean(accessToken),
    retry: 0,
    refetchOnWindowFocus: false,
  });
}