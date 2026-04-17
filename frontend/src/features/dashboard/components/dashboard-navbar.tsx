"use client";

import { motion } from "framer-motion";
import {
  ClipboardList,
  LayoutDashboard,
  MessageSquare,
  TrendingUp,
  User,
  Utensils,
} from "lucide-react";

import { cn } from "@/lib/utils/cn";

type DashboardNavbarProps = {
  username: string;
};

export function DashboardNavbar({
  username,
}: Readonly<DashboardNavbarProps>) {
  const navItems = [
    { name: "Dashboard", icon: LayoutDashboard, active: true },
    { name: "Meals", icon: Utensils, active: false },
    { name: "Log Food", icon: ClipboardList, active: false },
    { name: "Progress", icon: TrendingUp, active: false },
    { name: "AI Assistant", icon: MessageSquare, active: false },
  ];

  const initials =
    username.trim().length > 0 ? username.trim().slice(0, 1).toUpperCase() : "U";

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ type: "spring", stiffness: 50, damping: 20 }}
      className="dashboard-glass sticky top-0 z-50 flex items-center justify-between px-8 py-5"
    >
      <div className="flex items-center gap-2">
        <span className="font-display text-2xl font-extrabold tracking-tight text-primary">
          FitFuel AI
        </span>
      </div>

      <div className="hidden items-center gap-8 md:flex">
        {navItems.map((item) => (
          <button
            key={item.name}
            type="button"
            className="group relative cursor-default"
          >
            <span
              className={cn(
                "text-sm font-medium transition-colors",
                item.active
                  ? "dashboard-glow-green text-primary"
                  : "text-muted-foreground group-hover:text-heading"
              )}
            >
              {item.name}
            </span>

            {item.active ? (
              <motion.div
                layoutId="dashboard-nav-active"
                className="dashboard-glow-green absolute -bottom-1 left-0 right-0 h-0.5 bg-primary"
                initial={false}
              />
            ) : null}
          </button>
        ))}
      </div>

      <div className="flex items-center gap-4">
        <div className="flex h-10 w-10 items-center justify-center rounded-full border border-surface-high bg-surface-low text-heading transition-colors hover:bg-surface-high">
          <span className="text-sm font-black">{initials}</span>
        </div>

        <button
          type="button"
          aria-label="User menu"
          className="hidden h-10 w-10 items-center justify-center rounded-full border border-surface-high text-heading transition-colors hover:bg-surface-high md:flex"
        >
          <User className="h-5 w-5" />
        </button>
      </div>
    </motion.nav>
  );
}