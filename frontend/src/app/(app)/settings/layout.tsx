import type { ReactNode } from "react";

import { SettingsShell } from "@/features/settings/layout/settings-shell";

export default function SettingsLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return <SettingsShell>{children}</SettingsShell>;
}