export type OnboardingStatus = {
  hasProfile: boolean;
  hasGoal: boolean;
  isComplete: boolean;
  nextRoute: "/welcome" | "/dashboard";
};