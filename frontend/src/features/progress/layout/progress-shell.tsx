"use client";

import type { ReactNode } from "react";

import { ProgressBackground } from "@/features/progress/layout/progress-background";
import { ProgressMobileSubnav } from "@/features/progress/layout/progress-mobile-subnav";
import { ProgressSidebar } from "@/features/progress/layout/progress-sidebar";

export function ProgressShell({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <div className="relative min-h-screen bg-[#0c1322] text-white">
      <ProgressBackground />

      <ProgressSidebar />

      <main className="relative z-10 px-4 pb-24 pt-24 md:px-8 lg:ml-64 lg:px-10 lg:pb-12">
        <ProgressMobileSubnav />
        {children}
      </main>
    </div>
  );
}