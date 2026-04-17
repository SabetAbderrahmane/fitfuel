"use client";

import type { ReactNode } from "react";
import { motion } from "framer-motion";

import { SettingsMobileTabs } from "@/features/settings/layout/settings-mobile-tabs";
import { SettingsSidebar } from "@/features/settings/layout/settings-sidebar";

export function SettingsShell({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <div className="relative min-h-screen overflow-hidden bg-[#091224] text-white">
      <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(78,222,163,0.08),transparent_28%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_right,rgba(255,185,95,0.06),transparent_24%)]" />
        <motion.div
          animate={{ x: [0, 60, 0], y: [0, 40, 0] }}
          transition={{ duration: 16, repeat: Infinity, ease: "easeInOut" }}
          className="absolute right-[-120px] top-[100px] h-[340px] w-[340px] rounded-full bg-primary/10 blur-[120px]"
        />
        <motion.div
          animate={{ x: [0, -40, 0], y: [0, 50, 0] }}
          transition={{ duration: 14, repeat: Infinity, ease: "easeInOut" }}
          className="absolute bottom-[-80px] left-[22%] h-[280px] w-[280px] rounded-full bg-secondary/10 blur-[110px]"
        />
        <div className="absolute inset-0 bg-[linear-gradient(to_bottom,rgba(9,18,36,0.35),rgba(9,18,36,0.92))]" />
      </div>

      <SettingsSidebar />

      <main className="relative z-10 px-4 pb-14 pt-24 md:px-8 lg:ml-[280px] lg:px-12">
        <SettingsMobileTabs />
        {children}
      </main>
    </div>
  );
}