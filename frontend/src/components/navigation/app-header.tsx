"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  Bell,
  Bot,
  ClipboardList,
  LayoutDashboard,
  UtensilsCrossed,
} from "lucide-react";

import { cn } from "@/lib/utils/cn";

const navItems = [
  {
    label: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
    match: (pathname: string) => pathname.startsWith("/dashboard"),
  },
  {
    label: "Meals",
    href: "/meal-plans",
    icon: UtensilsCrossed,
    match: (pathname: string) => pathname.startsWith("/meal-plans"),
  },
  {
    label: "Log Food",
    href: "/food-log",
    icon: ClipboardList,
    match: (pathname: string) => pathname.startsWith("/food-log"),
  },
  {
    label: "Progress",
    href: "/progress",
    icon: Activity,
    match: (pathname: string) => pathname.startsWith("/progress"),
  },
  {
    label: "AI",
    href: "/assistant",
    icon: Bot,
    match: (pathname: string) => pathname.startsWith("/assistant"),
  },
] as const;

export function AppHeader() {
  const pathname = usePathname();

  return (
    <header className="fixed top-0 z-50 flex h-20 w-full items-center justify-between border-b border-primary/5 bg-background/40 px-8 backdrop-blur-3xl">
      <Link
        href="/dashboard"
        className="font-headline text-3xl font-black tracking-tighter text-primary"
      >
        FitFuel AI
      </Link>

      <nav className="hidden items-center gap-8 md:flex">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = item.match(pathname);

          return (
            <Link
              key={item.label}
              href={item.href}
              className="group relative flex items-center gap-2"
            >
              <Icon
                className={cn(
                  "h-4 w-4 transition-colors",
                  active ? "text-primary" : "text-slate-400 group-hover:text-primary"
                )}
              />
              <span
                className={cn(
                  "font-headline text-sm tracking-tight transition-all",
                  active
                    ? "font-extrabold text-primary"
                    : "font-semibold text-slate-400 group-hover:text-primary"
                )}
              >
                {item.label}
              </span>

              {active ? (
                <span className="absolute -bottom-2 left-0 h-0.5 w-full bg-primary" />
              ) : null}
            </Link>
          );
        })}
      </nav>

      <div className="flex items-center gap-5">
        <button
          type="button"
          aria-label="Notifications"
          className="text-slate-400 transition-colors hover:text-primary"
        >
          <Bell className="h-6 w-6" />
        </button>

        <div className="flex h-10 w-10 items-center justify-center overflow-hidden rounded-full border-2 border-primary bg-surface-container-highest shadow-[0_0_15px_rgba(78,222,163,0.3)]">
          <span className="text-sm font-black text-on-surface">U</span>
        </div>
      </div>
    </header>
  );
}