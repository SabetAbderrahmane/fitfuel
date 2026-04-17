"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Monitor,
  Moon,
  Palette,
  Smartphone,
  SunMedium,
} from "lucide-react";
import { cn } from "@/lib/utils/cn";

function GlassCard({
  children,
  className = "",
}: Readonly<{
  children: React.ReactNode;
  className?: string;
}>) {
  return (
    <div
      className={cn(
        "rounded-[2rem] border border-white/5 bg-[#141f34]/90 p-6 shadow-[0_20px_60px_rgba(0,0,0,0.28)] backdrop-blur-xl md:p-8",
        className
      )}
    >
      {children}
    </div>
  );
}

export function AppearanceSettingsPage() {
  const [theme, setTheme] = useState("Dark");
  const [density, setDensity] = useState("Comfortable");

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      className="space-y-8"
    >
      <section>
        <h1 className="font-headline text-4xl font-extrabold tracking-tight text-white md:text-5xl">
          Appearance
        </h1>
        <p className="mt-3 max-w-3xl text-lg text-slate-400">
          Personalize the look and feel of your FitFuel workspace.
        </p>
      </section>

      <div className="grid grid-cols-1 gap-8 xl:grid-cols-[1fr_1fr]">
        <GlassCard>
          <div className="mb-6 flex items-center gap-2 text-[11px] font-black uppercase tracking-[0.24em] text-primary">
            <Palette className="h-4 w-4" />
            Theme Mode
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            {[
              { label: "Dark", icon: Moon },
              { label: "Light", icon: SunMedium },
              { label: "System", icon: Monitor },
            ].map((item) => {
              const Icon = item.icon;
              const active = theme === item.label;

              return (
                <button
                  key={item.label}
                  onClick={() => setTheme(item.label)}
                  className={cn(
                    "rounded-[1.5rem] border p-5 text-left transition-all",
                    active
                      ? "border-primary/20 bg-primary/10 text-primary"
                      : "border-white/5 bg-white/[0.03] text-slate-300"
                  )}
                >
                  <Icon className="h-5 w-5" />
                  <div className="mt-5 text-xl font-black">{item.label}</div>
                </button>
              );
            })}
          </div>
        </GlassCard>

        <GlassCard>
          <div className="mb-6 text-[11px] font-black uppercase tracking-[0.24em] text-secondary">
            Interface Density
          </div>

          <div className="space-y-4">
            {["Compact", "Comfortable", "Expanded"].map((option) => {
              const active = density === option;

              return (
                <button
                  key={option}
                  onClick={() => setDensity(option)}
                  className={cn(
                    "flex w-full items-center justify-between rounded-2xl border px-5 py-4 text-left transition-all",
                    active
                      ? "border-secondary/20 bg-secondary/10 text-secondary"
                      : "border-white/5 bg-white/[0.03] text-white"
                  )}
                >
                  <span className="font-bold">{option}</span>
                  <span className="text-sm text-slate-400">
                    {option === "Compact"
                      ? "Higher information density"
                      : option === "Comfortable"
                      ? "Balanced spacing"
                      : "More breathing room"}
                  </span>
                </button>
              );
            })}
          </div>
        </GlassCard>
      </div>

      <GlassCard>
        <div className="mb-6 text-[11px] font-black uppercase tracking-[0.24em] text-primary">
          Preview
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {[
            "Dashboard Cards",
            "Charts & Insights",
            "Mobile Layout",
          ].map((title, index) => (
            <div
              key={title}
              className={cn(
                "rounded-[1.5rem] border border-white/5 p-5",
                index === 2 ? "bg-primary/10" : "bg-white/[0.03]"
              )}
            >
              <div className="flex items-center gap-2 text-sm font-black text-white">
                {index === 2 ? (
                  <Smartphone className="h-4 w-4 text-primary" />
                ) : (
                  <Monitor className="h-4 w-4 text-slate-300" />
                )}
                {title}
              </div>

              <div className="mt-5 space-y-3">
                <div className="h-4 rounded-full bg-white/10" />
                <div className="h-10 rounded-2xl bg-white/5" />
                <div className="grid grid-cols-3 gap-2">
                  <div className="h-16 rounded-2xl bg-white/5" />
                  <div className="h-16 rounded-2xl bg-white/5" />
                  <div className="h-16 rounded-2xl bg-white/5" />
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-8 flex justify-end">
          <button className="rounded-full bg-primary px-8 py-3 text-base font-black text-[#062315]">
            Apply Appearance
          </button>
        </div>
      </GlassCard>
    </motion.div>
  );
}