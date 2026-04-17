"use client";

import { motion } from "framer-motion";
import {
  Bell,
  Bot,
  CalendarClock,
  Mail,
  Smartphone,
} from "lucide-react";

function GlassCard({
  children,
  className = "",
}: Readonly<{
  children: React.ReactNode;
  className?: string;
}>) {
  return (
    <div
      className={`rounded-[2rem] border border-white/5 bg-[#141f34]/90 p-6 shadow-[0_20px_60px_rgba(0,0,0,0.28)] backdrop-blur-xl md:p-8 ${className}`}
    >
      {children}
    </div>
  );
}

function ToggleRow({
  title,
  subtitle,
  icon,
  enabled = true,
}: Readonly<{
  title: string;
  subtitle: string;
  icon: React.ReactNode;
  enabled?: boolean;
}>) {
  return (
    <div className="flex items-center justify-between rounded-2xl border border-white/5 bg-white/[0.03] px-5 py-4">
      <div className="flex items-start gap-4">
        <div className="mt-1 text-primary">{icon}</div>
        <div>
          <div className="text-lg font-bold text-white">{title}</div>
          <div className="mt-1 text-sm text-slate-400">{subtitle}</div>
        </div>
      </div>

      <div
        className={`h-7 w-12 rounded-full p-1 transition-colors ${
          enabled ? "bg-primary/30" : "bg-white/10"
        }`}
      >
        <div
          className={`h-5 w-5 rounded-full transition-all ${
            enabled ? "ml-auto bg-primary" : "bg-slate-500"
          }`}
        />
      </div>
    </div>
  );
}

export function NotificationsSettingsPage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      className="space-y-8"
    >
      <section>
        <h1 className="font-headline text-4xl font-extrabold tracking-tight text-white md:text-5xl">
          Notifications
        </h1>
        <p className="mt-3 max-w-3xl text-lg text-slate-400">
          Control reminders, weekly reports, and AI assistant nudges.
        </p>
      </section>

      <div className="grid grid-cols-1 gap-8 xl:grid-cols-[1fr_1fr]">
        <GlassCard>
          <div className="mb-6 text-[11px] font-black uppercase tracking-[0.24em] text-primary">
            Daily Reminders
          </div>

          <div className="space-y-4">
            <ToggleRow
              title="Meal Logging Reminder"
              subtitle="Prompt me if I haven’t logged meals by lunch."
              icon={<Bell className="h-5 w-5" />}
            />
            <ToggleRow
              title="Hydration Reminder"
              subtitle="Nudge me to drink water throughout the day."
              icon={<Smartphone className="h-5 w-5" />}
            />
            <ToggleRow
              title="Workout Prep Reminder"
              subtitle="Alert me before training windows."
              icon={<CalendarClock className="h-5 w-5" />}
              enabled={false}
            />
          </div>
        </GlassCard>

        <GlassCard>
          <div className="mb-6 text-[11px] font-black uppercase tracking-[0.24em] text-secondary">
            AI & Reports
          </div>

          <div className="space-y-4">
            <ToggleRow
              title="Weekly AI Summary"
              subtitle="Receive a compact weekly performance breakdown."
              icon={<Bot className="h-5 w-5" />}
            />
            <ToggleRow
              title="Email Digest"
              subtitle="Send my progress snapshot to my email."
              icon={<Mail className="h-5 w-5" />}
              enabled={false}
            />
            <ToggleRow
              title="Goal Drift Alerts"
              subtitle="Warn me when I drift too far from macro targets."
              icon={<Bell className="h-5 w-5" />}
            />
          </div>

          <div className="mt-8 flex justify-end">
            <button className="rounded-full bg-primary px-8 py-3 text-base font-black text-[#062315]">
              Save Notification Rules
            </button>
          </div>
        </GlassCard>
      </div>
    </motion.div>
  );
}