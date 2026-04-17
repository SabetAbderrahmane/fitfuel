"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  Droplets,
  Flame,
  Footprints,
  HelpCircle,
  LogOut,
  Weight,
} from "lucide-react";

import { cn } from "@/lib/utils/cn";

type ProgressNavItem = {
  href: string;
  label: string;
  icon: typeof Weight;
};

const navItems: ProgressNavItem[] = [
  {
    href: "/progress/weight-goal",
    label: "Weight Goal",
    icon: Weight,
  },
  {
    href: "/progress",
    label: "Daily Calories",
    icon: Flame,
  },
  {
    href: "/progress/water-intake",
    label: "Water Intake",
    icon: Droplets,
  },
  {
    href: "/progress/steps",
    label: "Steps",
    icon: Footprints,
  },
];

function isActive(pathname: string, href: string) {
  if (href === "/progress") {
    return pathname === "/progress";
  }

  return pathname.startsWith(href);
}

export function ProgressSidebar() {
  const pathname = usePathname();

  return (
    <motion.aside
      initial={{ x: -100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
      className="fixed left-0 top-0 z-40 hidden h-screen w-64 flex-col border-r border-white/5 bg-[#0c1322]/90 pt-24 backdrop-blur-xl lg:flex"
    >
      <div className="mb-8 px-6">
        <div className="group flex cursor-pointer items-center gap-3 rounded-2xl border border-white/10 bg-white/5 p-2 transition-colors hover:bg-white/10">
          <div className="h-12 w-12 overflow-hidden rounded-xl border border-white/10 bg-[#141b2b]">
            <img
              alt="User profile"
              src="https://picsum.photos/seed/fitfuel-progress-user/200"
              className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
              referrerPolicy="no-referrer"
            />
          </div>

          <div>
            <h3 className="text-sm font-bold text-white">Sabet</h3>
            <p className="text-xs uppercase tracking-tight text-slate-400">
              Progress Lab
            </p>
          </div>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-4">
        {navItems.map((item, idx) => {
          const active = isActive(pathname, item.href);
          const Icon = item.icon;

          return (
            <motion.div
              key={item.href}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 + idx * 0.08 }}
            >
              <Link
                href={item.href}
                className={cn(
                  "group relative flex w-full items-center gap-3 rounded-full px-5 py-4 text-sm font-semibold transition-all duration-300",
                  active
                    ? "text-primary"
                    : "text-slate-400 hover:bg-white/5 hover:text-white"
                )}
              >
                {active ? (
                  <motion.div
                    layoutId="progress-sidebar-pill"
                    className="absolute inset-0 rounded-full border border-primary/20 bg-primary/10"
                  />
                ) : null}

                <Icon
                  className={cn(
                    "relative z-10 h-5 w-5 transition-transform group-hover:scale-110",
                    active ? "text-primary" : ""
                  )}
                />
                <span className="relative z-10">{item.label}</span>
              </Link>
            </motion.div>
          );
        })}
      </nav>

      <div className="mt-auto space-y-1 px-4 pb-6">
        <button className="flex w-full items-center gap-3 rounded-full px-5 py-4 text-sm font-semibold text-slate-400 transition-all hover:bg-white/5 hover:text-white">
          <HelpCircle className="h-5 w-5 transition-transform group-hover:rotate-12" />
          <span>Help</span>
        </button>

        <button className="flex w-full items-center gap-3 rounded-full px-5 py-4 text-sm font-semibold text-slate-400 transition-all hover:bg-white/5 hover:text-white">
          <LogOut className="h-5 w-5 transition-transform group-hover:translate-x-1" />
          <span>Logout</span>
        </button>
      </div>
    </motion.aside>
  );
}