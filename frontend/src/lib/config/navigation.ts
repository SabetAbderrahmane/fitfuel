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
