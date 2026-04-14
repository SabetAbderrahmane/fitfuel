"use client";

import { Loader2 } from "lucide-react";

import { cn } from "@/lib/utils/cn";

type LoadingStateProps = {
  label?: string;
  className?: string;
};

export function LoadingState({
  label = "Loading...",
  className,
}: LoadingStateProps) {
  return (
    <span className={cn("inline-flex items-center gap-2", className)}>
      <Loader2 className="h-4 w-4 animate-spin" />
      <span>{label}</span>
    </span>
  );
}