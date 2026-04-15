"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  Utensils,
  Calendar,
  Activity,
  Zap,
  Dumbbell,
  HelpCircle,
} from "lucide-react";
import { ReactNode } from "react";

import { LoginForm } from "@/features/auth/forms/login-form";

const HERO_IMAGE_SRC = "/images/auth/loginbackground.png";

export default function LoginPage() {
  return (
    <div className="min-h-screen flex flex-col md:flex-row overflow-hidden bg-background">
      <Navbar />

      <section className="relative w-full md:w-3/5 min-h-[512px] md:min-h-screen kinetic-bg p-8 md:p-16 flex flex-col justify-center overflow-hidden">
        <div className="absolute inset-0 z-0 opacity-20">
          <img
            className="w-full h-full object-cover"
            alt="Athlete training"
            src={HERO_IMAGE_SRC}
          />
        </div>

        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="relative z-10 space-y-8 max-w-2xl"
        >
          <h1 className="font-headline text-5xl md:text-7xl font-black tracking-tighter leading-none text-white">
            Track <span className="text-primary text-glow">smarter.</span>
            <br />
            Eat <span className="text-secondary">better.</span>
            <br />
            Move <span className="text-primary text-glow">stronger.</span>
          </h1>

          <p className="text-xl text-on-surface-variant leading-relaxed font-medium">
            AI-powered meal planning, instant photo calorie estimation, and
            personalized fitness tracking.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-12">
            <FeatureCard
              icon={<Utensils className="text-on-primary-container" size={24} />}
              iconBg="bg-primary-container"
              title="ResNet50 AI Food Detection"
              description="Snap a photo and let our vision model identify macros instantly."
            />
            <FeatureCard
              icon={<Calendar className="text-on-secondary-container" size={24} />}
              iconBg="bg-secondary-container"
              title="Personalized Meal Plans"
              description="Adaptive fueling strategies synced directly with your training volume."
            />
            <FeatureCard
              icon={<Activity className="text-on-tertiary-container" size={24} />}
              iconBg="bg-tertiary-container"
              title="Real-time Progress Insights"
              description="Visual data streams that evolve as you hit your benchmarks."
              fullWidth
            />
          </div>

          <div className="mt-12 flex flex-wrap gap-6">
            <ProgressBadge label="Daily Goal" value="2,450 kcal" progress={70} />
            <ProgressBadge
              label="Protein"
              value="180g / 200g"
              icon={<Zap className="text-secondary" size={20} />}
            />
          </div>
        </motion.div>
      </section>

      <section className="w-full md:w-2/5 p-8 md:p-16 flex flex-col justify-center items-center relative">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="w-full max-w-md glass-panel p-10 rounded-lg shadow-2xl relative overflow-hidden group"
        >
          <div className="flex flex-col items-center mb-10">
            <div className="w-16 h-16 bg-primary rounded-2xl flex items-center justify-center mb-4 transform group-hover:rotate-6 transition-transform">
              <Dumbbell className="text-on-primary" size={36} />
            </div>
            <span className="font-headline text-2xl font-black tracking-tighter text-primary">
              FitFuel AI
            </span>
          </div>

          <div className="text-center mb-8">
            <h2 className="font-headline text-3xl font-bold text-white tracking-tight">
              Welcome back
            </h2>
            <p className="text-on-surface-variant mt-2">
              Log in to your performance dashboard
            </p>
          </div>

          <LoginForm />

          <div className="relative my-8 flex items-center">
            <div className="flex-grow border-t border-outline-variant/30" />
            <span className="flex-shrink mx-4 text-xs font-bold text-on-surface-variant uppercase tracking-widest">
              Or continue with
            </span>
            <div className="flex-grow border-t border-outline-variant/30" />
          </div>

          <button
            className="w-full bg-surface-container-highest text-on-surface font-bold py-4 rounded-full border border-outline-variant/20 hover:bg-surface-bright hover:border-outline-variant/40 transition-all flex items-center justify-center gap-3"
            type="button"
            disabled
          >
            <GoogleIcon />
            Google
          </button>

          <p className="text-center mt-10 text-sm text-on-surface-variant">
            Don&apos;t have an account?
            <Link
              className="text-primary font-bold hover:underline ml-1 transition-all"
              href="/sign-up"
            >
              Sign up
            </Link>
          </p>
        </motion.div>

        <div className="mt-8 flex gap-6 opacity-40 hover:opacity-100 transition-opacity">
          <Link
            className="text-xs font-normal text-on-surface hover:text-primary transition-colors"
            href="/login#privacy"
          >
            Privacy Policy
          </Link>
          <Link
            className="text-xs font-normal text-on-surface hover:text-primary transition-colors"
            href="/login#terms"
          >
            Terms of Service
          </Link>
          <Link
            className="text-xs font-normal text-on-surface hover:text-primary transition-colors"
            href="/login#support"
          >
            Support
          </Link>
        </div>
      </section>

      <Footer />
    </div>
  );
}

function Navbar() {
  return (
    <nav className="fixed top-0 w-full flex justify-between items-center px-8 py-6 z-50 bg-transparent backdrop-blur-xl">
      <div className="text-2xl font-black tracking-tighter text-primary font-headline">
        FitFuel AI
      </div>

      <div className="hidden md:flex space-x-8 items-center">
        <Link
          className="font-headline text-sm font-bold text-primary hover:text-primary/80 transition-colors active:scale-95 duration-200"
          href="/login"
        >
          Login
        </Link>
        <Link
          className="font-headline text-sm font-medium text-on-surface-variant hover:text-primary transition-colors active:scale-95 duration-200"
          href="/sign-up"
        >
          Join Beta
        </Link>
        <div className="h-4 w-[1px] bg-outline-variant/30 mx-2" />
        <button className="text-on-surface-variant hover:text-primary transition-colors">
          <HelpCircle size={20} />
        </button>
      </div>
    </nav>
  );
}

function Footer() {
  return (
    <footer className="fixed bottom-0 w-full flex flex-row justify-center space-x-6 pb-8 z-50 bg-transparent pointer-events-none">
      <span className="text-xs font-normal text-on-surface-variant/50">
        © 2024 FitFuel AI. All rights reserved.
      </span>
    </footer>
  );
}

function FeatureCard({
  icon,
  iconBg,
  title,
  description,
  fullWidth = false,
}: {
  icon: ReactNode;
  iconBg: string;
  title: string;
  description: string;
  fullWidth?: boolean;
}) {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className={`p-6 rounded-lg bg-surface-container-low transition-all hover:bg-surface-container-high group ${
        fullWidth ? "md:col-span-2 flex items-center gap-6" : ""
      }`}
    >
      <div
        className={`w-12 h-12 rounded-full ${iconBg} flex items-center justify-center mb-4 shrink-0`}
      >
        {icon}
      </div>
      <div>
        <h3 className="font-headline text-lg font-bold text-white mb-2">
          {title}
        </h3>
        <p className="text-sm text-on-surface-variant">{description}</p>
      </div>
    </motion.div>
  );
}

function ProgressBadge({
  label,
  value,
  progress,
  icon,
}: {
  label: string;
  value: string;
  progress?: number;
  icon?: ReactNode;
}) {
  return (
    <div className="flex items-center space-x-3 bg-surface-container-highest/40 px-5 py-3 rounded-full border border-outline-variant/10">
      {progress !== undefined ? (
        <div className="relative w-10 h-10">
          <svg className="w-full h-full transform -rotate-90">
            <circle
              className="text-surface-container-highest"
              cx="20"
              cy="20"
              fill="transparent"
              r="18"
              stroke="currentColor"
              strokeWidth="4"
            />
            <circle
              className="text-primary"
              cx="20"
              cy="20"
              fill="transparent"
              r="18"
              stroke="currentColor"
              strokeDasharray="113"
              strokeDashoffset={113 - (113 * progress) / 100}
              strokeWidth="4"
            />
          </svg>
        </div>
      ) : (
        icon
      )}
      <div>
        <p className="text-[10px] uppercase tracking-widest text-on-surface-variant font-bold">
          {label}
        </p>
        <p className="text-sm font-bold text-white">{value}</p>
      </div>
    </div>
  );
}

function GoogleIcon() {
  return (
    <svg className="w-5 h-5" viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
        fill="#4285F4"
      />
      <path
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
        fill="#34A853"
      />
      <path
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"
        fill="#FBBC05"
      />
      <path
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84C6.71 7.31 9.14 5.38 12 5.38z"
        fill="#EA4335"
      />
    </svg>
  );
}