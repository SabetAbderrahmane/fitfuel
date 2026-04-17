"use client";

import type { ReactNode } from "react";

import { AppHeader } from "@/components/navigation/app-header";
import { AppMobileNav } from "@/components/navigation/app-mobile-nav";

export function AppShell({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <div className="min-h-screen bg-background text-on-surface">
      <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
        <div className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage:
              'url("data:image/svg+xml,%3Csvg viewBox=\'0 0 200 200\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noiseFilter\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.65\' numOctaves=\'3\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23noiseFilter)\'/%3E%3C/svg%3E")',
          }}
        />
        <div className="absolute left-[-10%] top-[-10%] h-72 w-72 rounded-full bg-primary/5 blur-[120px]" />
        <div className="absolute bottom-[10%] right-[-5%] h-72 w-72 rounded-full bg-secondary/5 blur-[120px]" />
      </div>

      <AppHeader />

      <div className="relative z-10 min-h-screen pt-20 pb-24 md:pb-10">
        {children}
      </div>

      <AppMobileNav />
    </div>
  );
}