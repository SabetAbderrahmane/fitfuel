import type { LucideIcon } from "lucide-react";
import {
  BellRing,
  CircleUserRound,
  Goal,
  Palette,
  ShieldCheck,
  UserCog,
} from "lucide-react";

export type SettingsNavItem = {
  href: string;
  label: string;
  icon: LucideIcon;
  description: string;
};

export const settingsNavItems: SettingsNavItem[] = [
  {
    href: "/settings/profile",
    label: "Profile",
    icon: CircleUserRound,
    description: "Personal details and avatar",
  },
  {
    href: "/settings/goals-preferences",
    label: "Goals & Preferences",
    icon: Goal,
    description: "Nutrition targets and food preferences",
  },
  {
    href: "/settings/notifications",
    label: "Notifications",
    icon: BellRing,
    description: "Reminders and updates",
  },
  {
    href: "/settings/privacy-security",
    label: "Privacy & Security",
    icon: ShieldCheck,
    description: "Sessions, privacy, and protection",
  },
  {
    href: "/settings/account",
    label: "Account",
    icon: UserCog,
    description: "Plan, billing, and integrations",
  },
  {
    href: "/settings/appearance",
    label: "Appearance",
    icon: Palette,
    description: "Theme and dashboard feel",
  },
];

export const profileStatCards = [
  {
    label: "Kinetic Energy Score",
    value: "1,420",
    tone: "primary" as const,
  },
  {
    label: "Active Streak",
    value: "24d",
    tone: "secondary" as const,
  },
  {
    label: "AVG BPM",
    value: "72",
    tone: "solid" as const,
  },
];