import type { ReactNode } from "react";
import Link from "next/link";
import { HelpCircle } from "lucide-react";

export default function AuthLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <div className="relative min-h-screen overflow-hidden bg-[#04111f] text-white">
      <div className="absolute inset-0 bg-[linear-gradient(135deg,#061420_0%,#071425_35%,#07122a_58%,#16131d_100%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(16,185,129,0.24),transparent_28%),radial-gradient(circle_at_top_right,rgba(10,35,71,0.5),transparent_28%),radial-gradient(circle_at_bottom_right,rgba(245,158,11,0.10),transparent_32%)]" />
      <div className="absolute inset-y-0 left-0 w-lg bg-[radial-gradient(circle_at_center,rgba(16,185,129,0.10),transparent_62%)] blur-3xl" />
      <div className="absolute inset-y-0 right-0 w-120 bg-[radial-gradient(circle_at_center,rgba(245,158,11,0.08),transparent_62%)] blur-3xl" />

      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute left-[5%] top-[36%] -rotate-11 text-[clamp(5rem,18vw,16rem)] font-black italic tracking-[-0.08em] text-emerald-500/8">
          FOOD
        </div>
        <div className="absolute bottom-[14%] right-[2%] rotate-[8deg] text-[clamp(5rem,18vw,16rem)] font-black italic tracking-[-0.08em] text-white/5">
          POWER
        </div>
      </div>

      <header className="relative z-10 flex items-center justify-between px-6 py-6 sm:px-10 lg:px-12">
        <Link
          href="/login"
          className="text-2xl font-semibold italic tracking-tight text-emerald-400 drop-shadow-[0_0_16px_rgba(16,185,129,0.18)] sm:text-3xl"
        >
          FitFuel AI
        </Link>

        <button
          type="button"
          aria-label="Help"
          className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-white/10 bg-white/10 text-slate-200 backdrop-blur-xl transition hover:bg-white/15"
        >
          <HelpCircle className="h-5 w-5" />
        </button>
      </header>

      <main className="relative z-10 flex min-h-[calc(100vh-10rem)] items-center justify-center px-4 pb-24 pt-4 sm:px-6 lg:px-8">
        {children}
      </main>

      <footer className="relative z-10 hidden items-center justify-center gap-6 px-6 pb-8 text-[11px] uppercase tracking-[0.28em] text-slate-400/70 md:flex">
        <span>© 2026 FitFuel AI. Fuel your performance.</span>
        <Link href="/login#privacy" className="transition hover:text-slate-200">
          Privacy Policy
        </Link>
        <Link href="/login#terms" className="transition hover:text-slate-200">
          Terms of Service
        </Link>
        <Link href="/login#support" className="transition hover:text-slate-200">
          Contact Support
        </Link>
      </footer>
    </div>
  );
}