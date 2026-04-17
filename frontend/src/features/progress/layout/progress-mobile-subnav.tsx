"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Flame, Droplets, Footprints, Weight } from "lucide-react";

import { cn } from "@/lib/utils/cn";

const items = [
  { href: "/progress/weight-goal", label: "Weight", icon: Weight },
  { href: "/progress", label: "Calories", icon: Flame },
  { href: "/progress/water-intake", label: "Water", icon: Droplets },
  { href: "/progress/steps", label: "Steps", icon: Footprints },
] as const;

function isActive(pathname: string, href: string) {
  if (href === "/progress") {
    return pathname === "/progress";
  }

  return pathname.startsWith(href);
}

export function ProgressMobileSubnav() {
  const pathname = usePathname();

  return (
    <div className="mb-6 flex gap-3 overflow-x-auto pb-2 lg:hidden">
      {items.map((item) => {
        const Icon = item.icon;
        const active = isActive(pathname, item.href);

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