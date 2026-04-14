param(
  [string]$TargetPath = ".\frontend"
)

$ErrorActionPreference = "Stop"

function Ensure-Directory {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Path $Path -Force | Out-Null
  }
}

function Write-TextFile {
  param(
    [string]$Path,
    [string]$Content
  )

  $parent = Split-Path -Parent $Path
  if ($parent) {
    Ensure-Directory -Path $parent
  }

  Set-Content -LiteralPath $Path -Value $Content -Encoding UTF8
}

$root = (Resolve-Path -LiteralPath ".").Path
$frontendPath = Join-Path $root $TargetPath

$directories = @(
  $frontendPath,
  "$frontendPath/public",
  "$frontendPath/public/icons",
  "$frontendPath/public/images",
  "$frontendPath/public/images/placeholders",
  "$frontendPath/src",
  "$frontendPath/src/app",
  "$frontendPath/src/app/(marketing)",
  "$frontendPath/src/app/(auth)",
  "$frontendPath/src/app/(auth)/login",
  "$frontendPath/src/app/(auth)/sign-up",
  "$frontendPath/src/app/(onboarding)",
  "$frontendPath/src/app/(onboarding)/personal-details",
  "$frontendPath/src/app/(onboarding)/goals",
  "$frontendPath/src/app/(onboarding)/plan",
  "$frontendPath/src/app/(app)",
  "$frontendPath/src/app/(app)/dashboard",
  "$frontendPath/src/app/(app)/meal-plans",
  "$frontendPath/src/app/(app)/food-log",
  "$frontendPath/src/app/(app)/photo-estimator",
  "$frontendPath/src/app/(app)/progress",
  "$frontendPath/src/app/(app)/assistant",
  "$frontendPath/src/app/(app)/settings",
  "$frontendPath/src/components",
  "$frontendPath/src/components/charts",
  "$frontendPath/src/components/feedback",
  "$frontendPath/src/components/layout",
  "$frontendPath/src/components/navigation",
  "$frontendPath/src/components/states",
  "$frontendPath/src/components/upload",
  "$frontendPath/src/components/ui",
  "$frontendPath/src/features",
  "$frontendPath/src/features/auth",
  "$frontendPath/src/features/auth/api",
  "$frontendPath/src/features/auth/components",
  "$frontendPath/src/features/auth/forms",
  "$frontendPath/src/features/auth/hooks",
  "$frontendPath/src/features/auth/schemas",
  "$frontendPath/src/features/auth/types",
  "$frontendPath/src/features/onboarding",
  "$frontendPath/src/features/onboarding/api",
  "$frontendPath/src/features/onboarding/components",
  "$frontendPath/src/features/onboarding/forms",
  "$frontendPath/src/features/onboarding/hooks",
  "$frontendPath/src/features/onboarding/schemas",
  "$frontendPath/src/features/onboarding/types",
  "$frontendPath/src/features/dashboard",
  "$frontendPath/src/features/dashboard/api",
  "$frontendPath/src/features/dashboard/components",
  "$frontendPath/src/features/dashboard/hooks",
  "$frontendPath/src/features/dashboard/types",
  "$frontendPath/src/features/meal-plans",
  "$frontendPath/src/features/meal-plans/api",
  "$frontendPath/src/features/meal-plans/components",
  "$frontendPath/src/features/meal-plans/hooks",
  "$frontendPath/src/features/meal-plans/schemas",
  "$frontendPath/src/features/meal-plans/types",
  "$frontendPath/src/features/food-logs",
  "$frontendPath/src/features/food-logs/api",
  "$frontendPath/src/features/food-logs/components",
  "$frontendPath/src/features/food-logs/hooks",
  "$frontendPath/src/features/food-logs/schemas",
  "$frontendPath/src/features/food-logs/types",
  "$frontendPath/src/features/photos",
  "$frontendPath/src/features/photos/api",
  "$frontendPath/src/features/photos/components",
  "$frontendPath/src/features/photos/hooks",
  "$frontendPath/src/features/photos/schemas",
  "$frontendPath/src/features/photos/types",
  "$frontendPath/src/features/progress",
  "$frontendPath/src/features/progress/api",
  "$frontendPath/src/features/progress/components",
  "$frontendPath/src/features/progress/hooks",
  "$frontendPath/src/features/progress/types",
  "$frontendPath/src/features/assistant",
  "$frontendPath/src/features/assistant/api",
  "$frontendPath/src/features/assistant/components",
  "$frontendPath/src/features/assistant/hooks",
  "$frontendPath/src/features/assistant/schemas",
  "$frontendPath/src/features/assistant/types",
  "$frontendPath/src/features/settings",
  "$frontendPath/src/features/settings/api",
  "$frontendPath/src/features/settings/components",
  "$frontendPath/src/features/settings/hooks",
  "$frontendPath/src/features/settings/schemas",
  "$frontendPath/src/features/settings/types",
  "$frontendPath/src/hooks",
  "$frontendPath/src/lib",
  "$frontendPath/src/lib/api",
  "$frontendPath/src/lib/auth",
  "$frontendPath/src/lib/config",
  "$frontendPath/src/lib/env",
  "$frontendPath/src/lib/query",
  "$frontendPath/src/lib/types",
  "$frontendPath/src/lib/utils"
)

foreach ($directory in $directories) {
  Ensure-Directory -Path $directory
}

$packageJson = @'
{
  "name": "fitfuel-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint .",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "@hookform/resolvers": "latest",
    "@radix-ui/react-slot": "latest",
    "@tanstack/react-query": "latest",
    "@tanstack/react-query-devtools": "latest",
    "class-variance-authority": "latest",
    "clsx": "latest",
    "framer-motion": "latest",
    "lucide-react": "latest",
    "next": "latest",
    "react": "latest",
    "react-dom": "latest",
    "react-hook-form": "latest",
    "recharts": "latest",
    "sonner": "latest",
    "tailwind-merge": "latest",
    "zod": "latest"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "latest",
    "@types/node": "latest",
    "@types/react": "latest",
    "@types/react-dom": "latest",
    "eslint": "latest",
    "eslint-config-next": "latest",
    "typescript": "latest"
  }
}
'@

$tsconfig = @'
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": false,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
'@

$nextConfig = @'
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
};

export default nextConfig;
'@

$postcssConfig = @'
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};
'@

$eslintConfig = @'
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  ...compat.extends("next/core-web-vitals", "next/typescript"),
];

export default eslintConfig;
'@

$componentsJson = @'
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "",
    "css": "src/app/globals.css",
    "baseColor": "neutral",
    "cssVariables": true,
    "prefix": ""
  },
  "iconLibrary": "lucide",
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils/cn",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  }
}
'@

$gitignore = @'
node_modules
.next
out
dist
coverage
.env.local
.env.development.local
.env.test.local
.env.production.local
.vercel
*.log
'@

$envExample = @'
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api/v1
'@

$readme = @'
# FitFuel Frontend

Frontend scaffold for FitFuel AI.

## Stack
- Next.js 15 App Router
- TypeScript (strict)
- Tailwind CSS v4
- shadcn/ui
- TanStack Query v5
- React Hook Form + Zod
- Recharts
- Framer Motion

## Routes Planned
- /
- /login
- /sign-up
- /personal-details
- /goals
- /plan
- /dashboard
- /meal-plans
- /food-log
- /photo-estimator
- /progress
- /assistant
- /settings

## Run later
1. npm install
2. npm run dev
'@

$uiPlan = @'
# UI Plan

## Source of truth
- UI-AGENTS.md
- BACKEND-API-SPEC.md
- Uploaded FitFuel sketches

## Screen order
1. Auth (welcome, sign up, login)
2. Onboarding (personal details, goals, generated plan)
3. Dashboard
4. Meal plans
5. Food log
6. Photo estimator
7. Progress
8. AI meal assistant
9. Settings

## Backend-first constraints
- Use only documented `/api/v1` endpoints.
- Centralized JWT handling.
- Every screen needs loading, error, empty, and success states.
- Photo flow must support correction before logging.
'@

$nextEnv = @'
/// <reference types="next" />
/// <reference types="next/image-types/global" />

// This file is auto-managed by Next.js.
'@

$middleware = @'
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(_request: NextRequest) {
  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/meal-plans/:path*",
    "/food-log/:path*",
    "/photo-estimator/:path*",
    "/progress/:path*",
    "/assistant/:path*",
    "/settings/:path*",
    "/personal-details/:path*",
    "/goals/:path*",
    "/plan/:path*"
  ],
};
'@

$rootLayout = @'
import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "FitFuel AI",
  description: "AI-powered nutrition and fitness tracking.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
'@

$providers = @'
"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { useState } from "react";
import { Toaster } from "sonner";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <Toaster richColors position="top-right" />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
'@

$globalsCss = @'
@import "tailwindcss";

:root {
  color-scheme: dark;
}

html,
body {
  min-height: 100%;
}

body {
  background: #07111f;
  color: #f8fafc;
  font-family: Arial, Helvetica, sans-serif;
}

* {
  box-sizing: border-box;
}

a {
  color: inherit;
  text-decoration: none;
}
'@

$appLoading = @'
export default function Loading() {
  return <div className="p-6 text-sm text-white/70">Loading FitFuel...</div>;
}
'@

$appNotFound = @'
export default function NotFound() {
  return <div className="p-6 text-sm text-white/70">Page not found.</div>;
}
'@

$marketingPage = @'
export default function LandingPage() {
  return <main className="p-6">Welcome screen placeholder.</main>;
}
'@

$groupLayout = @'
export default function GroupLayout({ children }: { children: React.ReactNode }) {
  return children;
}
'@

$routePage = @'
export default function Page() {
  return <main className="p-6">Screen scaffold placeholder.</main>;
}
'@

$appShell = @'
export function AppShell({ children }: { children: React.ReactNode }) {
  return <div className="min-h-screen">{children}</div>;
}
'@

$authShell = @'
export function AuthShell({ children }: { children: React.ReactNode }) {
  return <div className="min-h-screen">{children}</div>;
}
'@

$onboardingShell = @'
export function OnboardingShell({ children }: { children: React.ReactNode }) {
  return <div className="min-h-screen">{children}</div>;
}
'@

$appSidebar = @'
export function AppSidebar() {
  return <aside>Sidebar placeholder.</aside>;
}
'@

$appHeader = @'
export function AppHeader() {
  return <header>Header placeholder.</header>;
}
'@

$loadingState = @'
export function LoadingState({ label = "Loading..." }: { label?: string }) {
  return <div className="text-sm text-white/70">{label}</div>;
}
'@

$errorState = @'
export function ErrorState({ message = "Something went wrong." }: { message?: string }) {
  return <div className="text-sm text-red-300">{message}</div>;
}
'@

$emptyState = @'
export function EmptyState({ message = "Nothing here yet." }: { message?: string }) {
  return <div className="text-sm text-white/60">{message}</div>;
}
'@

$lineChartCard = @'
export function LineChartCard() {
  return <div>Chart placeholder.</div>;
}
'@

$photoDropzone = @'
export function PhotoDropzone() {
  return <div>Photo upload placeholder.</div>;
}
'@

$queryClientFile = @'
import { QueryClient } from "@tanstack/react-query";

export function makeQueryClient() {
  return new QueryClient();
}
'@

$queryKeys = @'
export const queryKeys = {
  auth: ["auth"] as const,
  profile: ["profile"] as const,
  goals: ["goals"] as const,
  mealPlans: ["meal-plans"] as const,
  foodLogs: ["food-logs"] as const,
  photos: ["photos"] as const,
  progress: ["progress"] as const,
  assistant: ["assistant"] as const,
};
'@

$envConfig = @'
const env = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1",
  appUrl: process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000",
};

export { env };
'@

$routesFile = @'
export const routes = {
  home: "/",
  login: "/login",
  signUp: "/sign-up",
  personalDetails: "/personal-details",
  goals: "/goals",
  plan: "/plan",
  dashboard: "/dashboard",
  mealPlans: "/meal-plans",
  foodLog: "/food-log",
  photoEstimator: "/photo-estimator",
  progress: "/progress",
  assistant: "/assistant",
  settings: "/settings",
} as const;
'@

$navigationFile = @'
import { routes } from "@/lib/config/routes";

export const appNavigation = [
  { label: "Dashboard", href: routes.dashboard },
  { label: "Meal Plans", href: routes.mealPlans },
  { label: "Food Log", href: routes.foodLog },
  { label: "Photo Estimator", href: routes.photoEstimator },
  { label: "Progress", href: routes.progress },
  { label: "Assistant", href: routes.assistant },
  { label: "Settings", href: routes.settings },
] as const;
'@

$apiClient = @'
import { env } from "@/lib/env/client";

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${env.apiBaseUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return (await response.json()) as T;
}
'@

$apiErrors = @'
export class ApiError extends Error {
  constructor(message: string, public readonly status?: number) {
    super(message);
    this.name = "ApiError";
  }
}
'@

$tokenStorage = @'
export const authCookieKeys = {
  accessToken: "fitfuel_access_token",
  refreshToken: "fitfuel_refresh_token",
} as const;
'@

$sessionFile = @'
export function isAuthenticated() {
  return false;
}
'@

$authHook = @'
export function useAuth() {
  return {
    isAuthenticated: false,
  };
}
'@

$useMobile = @'
export function useMobile() {
  return false;
}
'@

$cnUtil = @'
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
'@

$datesUtil = @'
export function formatDate(value: string | Date) {
  return new Date(value).toLocaleDateString();
}
'@

$numbersUtil = @'
export function formatNumber(value: number) {
  return new Intl.NumberFormat().format(value);
}
'@

$sharedTypes = @'
export type ApiListParams = {
  limit?: number;
  offset?: number;
};
'@

Write-TextFile -Path "$frontendPath/package.json" -Content $packageJson
Write-TextFile -Path "$frontendPath/tsconfig.json" -Content $tsconfig
Write-TextFile -Path "$frontendPath/next.config.ts" -Content $nextConfig
Write-TextFile -Path "$frontendPath/postcss.config.mjs" -Content $postcssConfig
Write-TextFile -Path "$frontendPath/eslint.config.mjs" -Content $eslintConfig
Write-TextFile -Path "$frontendPath/components.json" -Content $componentsJson
Write-TextFile -Path "$frontendPath/.gitignore" -Content $gitignore
Write-TextFile -Path "$frontendPath/.env.example" -Content $envExample
Write-TextFile -Path "$frontendPath/README.md" -Content $readme
Write-TextFile -Path "$frontendPath/UI-PLAN.md" -Content $uiPlan
Write-TextFile -Path "$frontendPath/next-env.d.ts" -Content $nextEnv
Write-TextFile -Path "$frontendPath/middleware.ts" -Content $middleware

Write-TextFile -Path "$frontendPath/src/app/layout.tsx" -Content $rootLayout
Write-TextFile -Path "$frontendPath/src/app/providers.tsx" -Content $providers
Write-TextFile -Path "$frontendPath/src/app/globals.css" -Content $globalsCss
Write-TextFile -Path "$frontendPath/src/app/loading.tsx" -Content $appLoading
Write-TextFile -Path "$frontendPath/src/app/not-found.tsx" -Content $appNotFound
Write-TextFile -Path "$frontendPath/src/app/(marketing)/page.tsx" -Content $marketingPage
Write-TextFile -Path "$frontendPath/src/app/(auth)/layout.tsx" -Content $groupLayout
Write-TextFile -Path "$frontendPath/src/app/(auth)/login/page.tsx" -Content $routePage
Write-TextFile -Path "$frontendPath/src/app/(auth)/sign-up/page.tsx" -Content $routePage
Write-TextFile -Path "$frontendPath/src/app/(onboarding)/layout.tsx" -Content $groupLayout
Write-TextFile -Path "$frontendPath/src/app/(onboarding)/personal-details/page.tsx" -Content $routePage
Write-TextFile -Path "$frontendPath/src/app/(onboarding)/goals/page.tsx" -Content $routePage
Write-TextFile -Path "$frontendPath/src/app/(onboarding)/plan/page.tsx" -Content $routePage
Write-TextFile -Path "$frontendPath/src/app/(app)/layout.tsx" -Content $groupLayout
Write-TextFile -Path "$frontendPath/src/app/(app)/dashboard/page.tsx" -Content $routePage
Write-TextFile -Path "$frontendPath/src/app/(app)/meal-plans/page.tsx" -Content $routePage
Write-TextFile -Path "$frontendPath/src/app/(app)/food-log/page.tsx" -Content $routePage
Write-TextFile -Path "$frontendPath/src/app/(app)/photo-estimator/page.tsx" -Content $routePage
Write-TextFile -Path "$frontendPath/src/app/(app)/progress/page.tsx" -Content $routePage
Write-TextFile -Path "$frontendPath/src/app/(app)/assistant/page.tsx" -Content $routePage
Write-TextFile -Path "$frontendPath/src/app/(app)/settings/page.tsx" -Content $routePage

Write-TextFile -Path "$frontendPath/src/components/layout/app-shell.tsx" -Content $appShell
Write-TextFile -Path "$frontendPath/src/components/layout/auth-shell.tsx" -Content $authShell
Write-TextFile -Path "$frontendPath/src/components/layout/onboarding-shell.tsx" -Content $onboardingShell
Write-TextFile -Path "$frontendPath/src/components/navigation/app-sidebar.tsx" -Content $appSidebar
Write-TextFile -Path "$frontendPath/src/components/navigation/app-header.tsx" -Content $appHeader
Write-TextFile -Path "$frontendPath/src/components/states/loading-state.tsx" -Content $loadingState
Write-TextFile -Path "$frontendPath/src/components/states/error-state.tsx" -Content $errorState
Write-TextFile -Path "$frontendPath/src/components/states/empty-state.tsx" -Content $emptyState
Write-TextFile -Path "$frontendPath/src/components/charts/line-chart-card.tsx" -Content $lineChartCard
Write-TextFile -Path "$frontendPath/src/components/upload/photo-dropzone.tsx" -Content $photoDropzone

Write-TextFile -Path "$frontendPath/src/lib/query/client.ts" -Content $queryClientFile
Write-TextFile -Path "$frontendPath/src/lib/query/keys.ts" -Content $queryKeys
Write-TextFile -Path "$frontendPath/src/lib/env/client.ts" -Content $envConfig
Write-TextFile -Path "$frontendPath/src/lib/config/routes.ts" -Content $routesFile
Write-TextFile -Path "$frontendPath/src/lib/config/navigation.ts" -Content $navigationFile
Write-TextFile -Path "$frontendPath/src/lib/api/client.ts" -Content $apiClient
Write-TextFile -Path "$frontendPath/src/lib/api/errors.ts" -Content $apiErrors
Write-TextFile -Path "$frontendPath/src/lib/auth/token-storage.ts" -Content $tokenStorage
Write-TextFile -Path "$frontendPath/src/lib/auth/session.ts" -Content $sessionFile
Write-TextFile -Path "$frontendPath/src/lib/utils/cn.ts" -Content $cnUtil
Write-TextFile -Path "$frontendPath/src/lib/utils/dates.ts" -Content $datesUtil
Write-TextFile -Path "$frontendPath/src/lib/utils/numbers.ts" -Content $numbersUtil
Write-TextFile -Path "$frontendPath/src/lib/types/shared.ts" -Content $sharedTypes

Write-TextFile -Path "$frontendPath/src/hooks/use-auth.ts" -Content $authHook
Write-TextFile -Path "$frontendPath/src/hooks/use-mobile.ts" -Content $useMobile

Write-Host "FitFuel frontend skeleton created at: $frontendPath"
