"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";

import { settingsNavItems } from "@/features/settings/data/settings.mock";
import { cn } from "@/lib/utils/cn";

export function SettingsSidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-30 hidden h-screen w-[280px] border-r border-white/5 bg-[#10192d]/80 pt-24 backdrop-blur-xl lg:block">
      <div className="flex h-full flex-col">
        <div className="px-6">
          <h2 className="text-[2rem] font-black tracking-tight text-white">
            Settings
          </h2>
          <p className="mt-1 text-xs font-black uppercase tracking-[0.22em] text-slate-500">
            Manage your sanctuary
          </p>
        </div>

        <nav className="mt-8 flex-1 space-y-2 px-4">
          {settingsNavItems.map((item, index) => {
            const active = pathname === item.href;
            const Icon = item.icon;

            return (
              <motion.div
                key={item.href}
                initial={{ opacity: 0, x: -14 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.4, delay: 0.08 + index * 0.05 }}
              >
                <Link
                  href={item.href}
                  className={cn(
                    "group relative flex items-center gap-3 overflow-hidden rounded-full px-4 py-3.5 text-sm font-semibold transition-all",
                    active
                      ? "text-primary"
                      : "text-slate-400 hover:bg-white/[0.03] hover:text-white"
                  )}
                >
                  {active ? (
                    <motion.div
                      layoutId="settings-sidebar-pill"
                      className="absolute inset-0 rounded-full border border-primary/20 bg-white/10"
                      transition={{ type: "spring", stiffness: 320, damping: 28 }}
                    />
                  ) : null}

                  <Icon className="relative z-10 h-5 w-5" />
                  <span className="relative z-10">{item.label}</span>
                </Link>
              </motion.div>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}