"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  Bot,
  LayoutDashboard,
  Plus,
  UtensilsCrossed,
} from "lucide-react";

import { cn } from "@/lib/utils/cn";

type MobileNavItem = {
  href: string;
  label: string;
  icon: typeof LayoutDashboard;
  primary?: boolean;
};

const items: MobileNavItem[] = [
  { href: "/dashboard", label: "Dash", icon: LayoutDashboard, primary: false },
  { href: "/meal-plans", label: "Meals", icon: UtensilsCrossed, primary: false },
  { href: "/food-log", label: "Log", icon: Plus, primary: true },
  { href: "/progress", label: "Stats", icon: Activity, primary: false },
  { href: "/assistant", label: "Coach", icon: Bot, primary: false },
];

export function AppMobileNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 flex h-20 items-center justify-around border-t border-primary/10 bg-background/60 px-4 backdrop-blur-3xl md:hidden">
      {items.map((item) => {
        const Icon = item.icon;
        const active = pathname.startsWith(item.href);

        if (item.primary) {
          return (
            <Link
              key={item.label}
              href={item.href}
              className="flex h-14 w-14 -translate-y-5 items-center justify-center rounded-full border-4 border-background bg-primary text-on-primary shadow-[0_8px_20px_rgba(78,222,163,0.4)]"
            >
              <Icon className="h-6 w-6" />
            </Link>
          );
        }

        return (
          <Link
            key={item.label}
            href={item.href}
            className="group flex flex-col items-center gap-1.5"
          >
            <Icon
              className={cn(
                "h-6 w-6 transition-transform group-hover:scale-110",
                active ? "text-primary" : "text-slate-400"
              )}
            />
            <span
              className={cn(
                "text-[10px] font-black uppercase tracking-tighter",
                active ? "text-primary" : "text-slate-400"
              )}
            >
              {item.label}
            </span>
          </Link>
        );
      })}
    </nav>
  );
}