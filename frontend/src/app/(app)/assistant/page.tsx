"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { AssistantScreen } from "@/features/assistant/components/assistant-screen";
import { getAccessToken } from "@/lib/auth/token-storage";

export default function AssistantPage() {
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
        <LoadingState
          label="Preparing your AI meal assistant..."
          className="text-primary"
        />
      </main>
    );
  }

  if (!accessToken) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background px-6">
        <ErrorState message="You must be signed in to use the AI meal assistant." />
      </main>
    );
  }

  return <AssistantScreen accessToken={accessToken} />;
}