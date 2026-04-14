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
