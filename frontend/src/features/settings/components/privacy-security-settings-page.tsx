"use client";

import { motion } from "framer-motion";
import {
  EyeOff,
  KeyRound,
  Laptop2,
  LockKeyhole,
  Shield,
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

export function PrivacySecuritySettingsPage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      className="space-y-8"
    >
      <section>
        <h1 className="font-headline text-4xl font-extrabold tracking-tight text-white md:text-5xl">
          Privacy & Security
        </h1>
        <p className="mt-3 max-w-3xl text-lg text-slate-400">
          Manage protection settings, session visibility, and recovery options.
        </p>
      </section>

      <div className="grid grid-cols-1 gap-8 xl:grid-cols-[1fr_1fr]">
        <GlassCard>
          <div className="mb-6 text-[11px] font-black uppercase tracking-[0.24em] text-primary">
            Protection
          </div>

          <div className="space-y-4">
            {[
              {
                icon: <LockKeyhole className="h-5 w-5 text-primary" />,
                title: "Change Password",
                subtitle: "Last updated 12 days ago",
              },
              {
                icon: <KeyRound className="h-5 w-5 text-secondary" />,
                title: "Two-Factor Authentication",
                subtitle: "Currently enabled",
              },
              {
                icon: <EyeOff className="h-5 w-5 text-slate-300" />,
                title: "Private Profile Mode",
                subtitle: "Hide profile details from public visibility",
              },
            ].map((item) => (
              <div
                key={item.title}
                className="flex items-center justify-between rounded-2xl border border-white/5 bg-white/[0.03] px-5 py-4"
              >
                <div className="flex items-center gap-4">
                  {item.icon}
                  <div>
                    <div className="text-lg font-bold text-white">{item.title}</div>
                    <div className="mt-1 text-sm text-slate-400">
                      {item.subtitle}
                    </div>
                  </div>
                </div>

                <button className="rounded-full bg-white/10 px-4 py-2 text-sm font-bold text-white">
                  Manage
                </button>
              </div>
            ))}
          </div>
        </GlassCard>

        <GlassCard>
          <div className="mb-6 text-[11px] font-black uppercase tracking-[0.24em] text-secondary">
            Active Sessions
          </div>

          <div className="space-y-4">
            {[
              {
                icon: <Laptop2 className="h-5 w-5 text-primary" />,
                title: "Windows Desktop · Tokyo",
                subtitle: "Current session · Chrome",
              },
              {
                icon: <Smartphone className="h-5 w-5 text-slate-300" />,
                title: "Android Device · Japan",
                subtitle: "Last active 2 hours ago",
              },
            ].map((session) => (
              <div
                key={session.title}
                className="flex items-center justify-between rounded-2xl border border-white/5 bg-white/[0.03] px-5 py-4"
              >
                <div className="flex items-center gap-4">
                  {session.icon}
                  <div>
                    <div className="text-lg font-bold text-white">
                      {session.title}
                    </div>
                    <div className="mt-1 text-sm text-slate-400">
                      {session.subtitle}
                    </div>
                  </div>
                </div>

                <button className="text-sm font-bold text-[#ffb4ab]">
                  Revoke
                </button>
              </div>
            ))}
          </div>

          <div className="mt-8 rounded-2xl border border-primary/10 bg-primary/10 px-5 py-4 text-sm text-primary">
            Security events are frontend-only here for now. You can wire real session
            and audit APIs later.
          </div>

          <div className="mt-6 flex items-center gap-2 text-sm text-slate-400">
            <Shield className="h-4 w-4 text-primary" />
            Your account is currently protected with elevated safeguards.
          </div>
        </GlassCard>
      </div>
    </motion.div>
  );
}