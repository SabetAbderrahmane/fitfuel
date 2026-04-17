import type {
  AssistantPageData,
  ChatMessageCreateRequest,
  ChatSessionCreateRequest,
  ChatSessionDetailResponse,
  ChatSessionSummaryResponse,
  ChatTurnResponse,
  ProgressSnapshotResponse,
  SendAssistantMessageResult,
  UserGoalResponse,
} from "@/features/assistant/types/assistant.types";

function getApiBaseUrl(): string {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();

  if (!baseUrl) {
    throw new Error(
      "NEXT_PUBLIC_API_BASE_URL is missing. Add it to frontend/.env.local."
    );
  }

  return baseUrl.replace(/\/$/, "");
}

function extractErrorMessage(payload: unknown): string | null {
  if (!payload || typeof payload !== "object" || !("detail" in payload)) {
    return null;
  }

  const detail = (payload as { detail?: unknown }).detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }

        if (
          item &&
          typeof item === "object" &&
          "msg" in item &&
          typeof (item as { msg?: unknown }).msg === "string"
        ) {
          return (item as { msg: string }).msg;
        }

        return null;
      })
      .filter((message): message is string => Boolean(message));

    return messages.length > 0 ? messages.join(", ") : null;
  }

  return null;
}

async function fetchJson<T>(
  path: string,
  accessToken: string,
  init?: RequestInit
): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${accessToken}`,
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  const responseBody: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(
      extractErrorMessage(responseBody) ?? `Request failed for ${path}.`
    );
  }

  return responseBody as T;
}

async function fetchMaybe404<T>(
  path: string,
  accessToken: string
): Promise<T | null> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    method: "GET",
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    cache: "no-store",
  });

  if (response.status === 404) {
    return null;
  }

  const responseBody: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(
      extractErrorMessage(responseBody) ?? `Request failed for ${path}.`
    );
  }

  return responseBody as T;
}

export async function createChatSession(
  accessToken: string,
  payload: ChatSessionCreateRequest
): Promise<ChatSessionSummaryResponse> {
  return fetchJson<ChatSessionSummaryResponse>("/api/v1/chat/sessions", accessToken, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export async function listChatSessions(
  accessToken: string,
  limit = 20,
  offset = 0
): Promise<ChatSessionSummaryResponse[]> {
  return fetchJson<ChatSessionSummaryResponse[]>(
    `/api/v1/chat/sessions?limit=${limit}&offset=${offset}`,
    accessToken
  );
}

export async function getChatSession(
  accessToken: string,
  chatSessionId: string
): Promise<ChatSessionDetailResponse> {
  return fetchJson<ChatSessionDetailResponse>(
    `/api/v1/chat/sessions/${chatSessionId}`,
    accessToken
  );
}

export async function sendChatMessage(
  accessToken: string,
  chatSessionId: string,
  payload: ChatMessageCreateRequest
): Promise<ChatTurnResponse> {
  return fetchJson<ChatTurnResponse>(
    `/api/v1/chat/sessions/${chatSessionId}/messages`,
    accessToken,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    }
  );
}

export async function fetchAssistantPageData(
  accessToken: string
): Promise<AssistantPageData> {
  const [sessionSummaries, currentGoal, snapshots] = await Promise.all([
    listChatSessions(accessToken, 20, 0),
    fetchMaybe404<UserGoalResponse>("/api/v1/goals/current", accessToken),
    fetchJson<ProgressSnapshotResponse[]>(
      "/api/v1/progress/snapshots?limit=1&offset=0",
      accessToken
    ),
  ]);

  const latestSessionSummary =
    [...sessionSummaries].sort(
      (a, b) =>
        new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    )[0] ?? null;

  const latestSessionDetail = latestSessionSummary
    ? await getChatSession(accessToken, latestSessionSummary.id)
    : null;

  return {
    latestSessionSummary,
    latestSessionDetail,
    currentGoal,
    latestSnapshot: snapshots[0] ?? null,
  };
}

export async function sendAssistantMessage(
  accessToken: string,
  sessionId: string | null,
  content: string
): Promise<SendAssistantMessageResult> {
  let resolvedSessionId = sessionId;

  if (!resolvedSessionId) {
    const createdSession = await createChatSession(accessToken, {
      title: "AI Meal Assistant",
    });

    resolvedSessionId = createdSession.id;
  }

  const turn = await sendChatMessage(accessToken, resolvedSessionId, {
    content,
  });

  return {
    sessionId: resolvedSessionId,
    turn,
  };
}