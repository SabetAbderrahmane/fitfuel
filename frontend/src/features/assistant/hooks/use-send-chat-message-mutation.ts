"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { sendAssistantMessage } from "@/features/assistant/api/assistant";
import type { SendAssistantMessageResult } from "@/features/assistant/types/assistant.types";

type Variables = {
  accessToken: string;
  sessionId: string | null;
  content: string;
};

export function useSendChatMessageMutation() {
  const queryClient = useQueryClient();

  return useMutation<SendAssistantMessageResult, Error, Variables>({
    mutationFn: async ({ accessToken, sessionId, content }) =>
      sendAssistantMessage(accessToken, sessionId, content),
    onSuccess: async (_data, variables) => {
      await queryClient.invalidateQueries({
        queryKey: ["assistant-page", variables.accessToken],
      });
    },
  });
}