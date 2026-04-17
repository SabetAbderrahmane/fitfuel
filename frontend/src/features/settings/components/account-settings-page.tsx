"use client";

import { motion } from "framer-motion";
import {
  CreditCard,
  Link2,
  Sparkles,
  Trash2,
  UserRoundX,
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

export function AccountSettingsPage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      className="space-y-8"
    >
      <section>
        <h1 className="font-headline text-4xl font-extrabold tracking-tight text-white md:text-5xl">
          Account
        </h1>
        <p className="mt-3 max-w-3xl text-lg text-slate-400">
          Review membership, connected services, and account-level actions.
        </p>
      </section>

      <div className="grid grid-cols-1 gap-8 xl:grid-cols-[1fr_1fr]">
        <GlassCard>
          <div className="mb-6 flex items-center gap-2 text-[11px] font-black uppercase tracking-[0.24em] text-secondary">
            <Sparkles className="h-4 w-4" />
            Plan & Billing
          </div>

          <div className="rounded-[1.5rem] border border-secondary/25 bg-secondary/10 p-6">
            <div className="text-2xl font-black text-secondary">FitFuel Pro</div>
            <div className="mt-2 text-slate-300">
              Unlimited AI meal suggestions, advanced analysis, and premium charts.
            </div>

            <div className="mt-6 flex flex-wrap gap-3">
              <button className="rounded-full bg-secondary px-6 py-3 text-base font-black text-[#2d1900]">
                Manage Plan
              </button>
              <button className="rounded-full border border-white/10 px-6 py-3 text-base font-bold text-white">
                View Invoices
              </button>
            </div>
          </div>

          <div className="mt-6 flex items-center gap-3 rounded-2xl bg-white/[0.03] px-5 py-4">
            <CreditCard className="h-5 w-5 text-primary" />
            <div>
              <div className="font-bold text-white">Billing Method</div>
              <div className="text-sm text-slate-400">Visa ending in 2048</div>
            </div>
          </div>
        </GlassCard>

        <GlassCard>
          <div className="mb-6 flex items-center gap-2 text-[11px] font-black uppercase tracking-[0.24em] text-primary">
            <Link2 className="h-4 w-4" />
            Connected Services
          </div>

          <div className="space-y-4">
            {[
              "Google Account",
              "Cloudinary Media Uploads",
              "Future Wearable Sync",
            ].map((item) => (
              <div
                key={item}
                className="flex items-center justify-between rounded-2xl border border-white/5 bg-white/[0.03] px-5 py-4"
              >
                <span className="font-bold text-white">{item}</span>
                <button className="rounded-full bg-white/10 px-4 py-2 text-sm font-bold text-white">
                  Configure
                </button>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>

      <GlassCard className="border-[#ffb4ab]/20 bg-[#2a1720]/70">
        <div className="mb-6 flex items-center gap-2 text-[11px] font-black uppercase tracking-[0.24em] text-[#ffb4ab]">
          <Trash2 className="h-4 w-4" />
          Danger Zone
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div className="rounded-2xl border border-[#ffb4ab]/15 bg-black/10 p-5">
            <div className="font-bold text-white">Deactivate Account</div>
            <div className="mt-2 text-sm text-slate-300">
              Hide your account temporarily without deleting data.
            </div>
            <button className="mt-5 rounded-full border border-[#ffb4ab]/30 px-5 py-2.5 text-sm font-bold text-[#ffb4ab]">
              Deactivate
            </button>
          </div>

          <div className="rounded-2xl border border-[#ffb4ab]/15 bg-black/10 p-5">
            <div className="flex items-center gap-2 font-bold text-white">
              <UserRoundX className="h-4 w-4 text-[#ffb4ab]" />
              Delete Account
            </div>
            <div className="mt-2 text-sm text-slate-300">
              Permanently remove your account and all associated data.
            </div>
            <button className="mt-5 rounded-full bg-[#ffb4ab] px-5 py-2.5 text-sm font-black text-[#35161d]">
              Delete Permanently
            </button>
          </div>
        </div>
      </GlassCard>
    </motion.div>
  );
}