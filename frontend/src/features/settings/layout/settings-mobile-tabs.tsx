"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { settingsNavItems } from "@/features/settings/data/settings.mock";
import { cn } from "@/lib/utils/cn";

export function SettingsMobileTabs() {
  const pathname = usePathname();

  return (
    <div className="mb-6 flex gap-3 overflow-x-auto pb-2 lg:hidden">
      {settingsNavItems.map((item) => {
        const Icon = item.icon;
        const active = pathname === item.href;

        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex shrink-0 items-center gap-2 rounded-full border px-4 py-2.5 text-xs font-black uppercase tracking-wider transition-all",
              active
                ? "border-primary/20 bg-primary/10 text-primary"
                : "border-white/5 bg-white/[0.03] text-slate-400"
            )}
          >
            <Icon className="h-4 w-4" />
            {item.label}
          </Link>
        );
      })}
    </div>
  );
}