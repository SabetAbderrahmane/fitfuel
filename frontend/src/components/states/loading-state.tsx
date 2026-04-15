"use client";

import { Loader2 } from "lucide-react";

type LoadingStateProps = {
  label?: string;
  className?: string;
};

export function LoadingState({
  label = "Loading...",
  className,
}: LoadingStateProps) {
  return (
    <span className={className ?? "inline-flex items-center gap-2"}>
      <Loader2 className="h-4 w-4 animate-spin" />
      <span>{label}</span>
    </span>
  );
}