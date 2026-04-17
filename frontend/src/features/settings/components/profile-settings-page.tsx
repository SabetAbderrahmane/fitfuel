"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  CalendarDays,
  HeartPulse,
  Info,
  Pencil,
  ShieldCheck,
  Timer,
  Zap,
} from "lucide-react";

import { profileStatCards } from "@/features/settings/data/settings.mock";
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
        "rounded-[2rem] border border-white/5 bg-[#141f34]/90 shadow-[0_20px_60px_rgba(0,0,0,0.28)] backdrop-blur-xl",
        className
      )}
    >
      {children}
    </div>
  );
}

function Field({
  label,
  children,
}: Readonly<{
  label: string;
  children: React.ReactNode;
}>) {
  return (
    <label className="block space-y-3">
      <span className="text-sm font-bold text-slate-300">{label}</span>
      {children}
    </label>
  );
}

export function ProfileSettingsPage() {
  const [fullName, setFullName] = useState("Alex Rivers");
  const [email, setEmail] = useState("alex@fitness.com");
  const [dateOfBirth, setDateOfBirth] = useState("1992-01-15");
  const [bio, setBio] = useState(
    "Fitness enthusiast on a journey to peak performance"
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      className="space-y-10"
    >
      <section>
        <h1 className="font-headline text-4xl font-extrabold tracking-tight text-white md:text-5xl">
          Profile Information
        </h1>
        <p className="mt-3 max-w-3xl text-lg text-slate-400">
          Update your personal details and how others see you on the FitFuel AI
          platform.
        </p>
      </section>

      <GlassCard className="p-6 md:p-10">
        <div className="flex flex-col gap-10">
          <div className="flex flex-col gap-6 border-b border-white/5 pb-8 md:flex-row md:items-center">
            <div className="relative h-32 w-32 shrink-0 rounded-full border border-white/10 bg-black shadow-[0_0_0_10px_rgba(255,255,255,0.02)]">
              <div className="absolute inset-[18px] rounded-full border border-primary/40 bg-[radial-gradient(circle_at_top,#235a6d,#102336_72%)]" />
              <button className="absolute bottom-1 right-1 flex h-10 w-10 items-center justify-center rounded-full bg-primary text-[#092016] shadow-[0_10px_20px_rgba(78,222,163,0.35)]">
                <Pencil className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-3">
              <h2 className="text-3xl font-black tracking-tight text-white">
                Your Avatar
              </h2>
              <p className="text-lg text-slate-400">
                JPG, GIF or PNG. Max size of 800K
              </p>

              <div className="flex flex-wrap items-center gap-4 pt-2">
                <button className="rounded-full bg-white/10 px-6 py-3 font-bold text-white transition-all hover:bg-white/15">
                  Upload New
                </button>
                <button className="font-bold text-[#ffb4ab] transition-opacity hover:opacity-80">
                  Remove
                </button>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
            <Field label="Full Name">
              <input
                value={fullName}
                onChange={(event) => setFullName(event.target.value)}
                className="h-16 w-full rounded-[1.25rem] border border-transparent bg-[#0d1830] px-6 text-xl font-medium text-white outline-none transition-colors focus:border-primary/20"
              />
            </Field>

            <Field label="Email Address">
              <input
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="h-16 w-full rounded-[1.25rem] border border-transparent bg-[#0d1830] px-6 text-xl font-medium text-white outline-none transition-colors focus:border-primary/20"
              />
            </Field>

            <Field label="Date of Birth">
              <div className="relative">
                <input
                  type="date"
                  value={dateOfBirth}
                  onChange={(event) => setDateOfBirth(event.target.value)}
                  className="h-16 w-full rounded-[1.25rem] border border-transparent bg-[#0d1830] px-6 pr-14 text-xl font-medium text-white outline-none transition-colors focus:border-primary/20"
                />
                <CalendarDays className="pointer-events-none absolute right-5 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
              </div>
            </Field>

            <Field label="Subscription Status">
              <div className="flex h-16 items-center justify-between rounded-[1.25rem] border border-secondary/30 bg-secondary/10 px-6">
                <div>
                  <div className="text-lg font-black text-secondary">
                    FitFuel Pro Member
                  </div>
                  <div className="text-sm font-medium text-slate-400">
                    Next billing: Feb 20, 2024
                  </div>
                </div>

                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-secondary/20 text-secondary">
                  <Zap className="h-4 w-4" />
                </div>
              </div>
            </Field>
          </div>

          <Field label="Bio">
            <textarea
              value={bio}
              onChange={(event) => setBio(event.target.value)}
              rows={4}
              className="w-full rounded-[1.5rem] border border-transparent bg-[#0d1830] px-6 py-5 text-xl font-medium text-white outline-none transition-colors focus:border-primary/20"
            />
          </Field>

          <div className="flex flex-col gap-5 border-t border-white/5 pt-6 md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <Info className="h-4 w-4 text-slate-500" />
              Your data is secured with end-to-end encryption.
            </div>

            <div className="flex flex-col gap-3 sm:flex-row">
              <button className="rounded-full px-6 py-3 text-lg font-bold text-white transition-opacity hover:opacity-80">
                Discard
              </button>
              <motion.button
                whileHover={{ scale: 1.02, y: -1 }}
                whileTap={{ scale: 0.98 }}
                className="rounded-full bg-primary px-10 py-3 text-lg font-black text-[#062315] shadow-[0_10px_24px_rgba(78,222,163,0.35)]"
              >
                Save Changes
              </motion.button>
            </div>
          </div>
        </div>
      </GlassCard>

      <section className="grid grid-cols-1 gap-6 md:grid-cols-3">
        {profileStatCards.map((card, index) => {
          const Icon =
            card.tone === "primary"
              ? Zap
              : card.tone === "secondary"
              ? Timer
              : HeartPulse;

          return (
            <motion.div
              key={card.label}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.08 + index * 0.08 }}
            >
              <GlassCard
                className={cn(
                  "h-full p-8",
                  card.tone === "solid" ? "bg-primary text-[#083223]" : ""
                )}
              >
                <Icon
                  className={cn(
                    "h-5 w-5",
                    card.tone === "primary"
                      ? "text-primary"
                      : card.tone === "secondary"
                      ? "text-secondary"
                      : "text-[#083223]"
                  )}
                />

                <div
                  className={cn(
                    "mt-6 font-headline text-5xl font-black",
                    card.tone === "solid" ? "text-[#083223]" : "text-white"
                  )}
                >
                  {card.value}
                </div>

                <div
                  className={cn(
                    "mt-2 text-sm font-black uppercase tracking-[0.22em]",
                    card.tone === "solid" ? "text-[#0b5033]/80" : "text-slate-400"
                  )}
                >
                  {card.label}
                </div>
              </GlassCard>
            </motion.div>
          );
        })}
      </section>
    </motion.div>
  );
}