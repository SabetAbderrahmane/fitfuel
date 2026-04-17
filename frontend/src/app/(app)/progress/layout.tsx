import type { ReactNode } from "react";

import { ProgressShell } from "@/features/progress/layout/progress-shell";

export default function ProgressLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return <ProgressShell>{children}</ProgressShell>;
}