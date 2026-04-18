# FitFuel AI(not finished yet tho it is still under work)

**A personal project built out of pain, discipline, and a desire to create something meaningful.**

An AI-powered nutrition and fitness tracking web application that helps you take control of your body and mind .

### What is FitFuel AI?

FitFuel AI lets you:
- Track your meals with smart AI photo calorie estimation (ResNet50)
- Get personalized meal plans and macro targets
- Log food manually or via photo
- Monitor your progress with beautiful charts
- Chat with an AI meal assistant
- Stay consistent even when motivation is gone

This project was built during one of the hardest periods of my life. It became my escape, my discipline, and my proof that I can still create something good even when everything else falls apart.

### Tech Stack

**Frontend**
- Next.js 15 (App Router)
- TypeScript (strict)
- Tailwind CSS + shadcn/ui
- TanStack Query v5
- React Hook Form + Zod
- Framer Motion

**Backend**
- FastAPI + Python
- PostgreSQL + SQLAlchemy
- JWT Authentication
- ResNet50 for food image recognition
- Cloudinary for image storage

### Features(not finished yet tho it is still under work)

- Split-screen modern authentication (login & sign-up)
- Onboarding flow with BMR/TDEE calculation
- AI Photo Calorie Estimator
- Personalized meal planning
- Progress tracking & analytics
- AI Meal Assistant chat
- Responsive design (mobile-first)

### How to Run Locally

```bash
# Clone the repo
git clone https://github.com/SabetAbderrahmane/fitfuel.git

# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (in another terminal)
cd frontend
npm install
npm run dev