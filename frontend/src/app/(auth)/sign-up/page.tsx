"use client";

import Link from "next/link";
import { ReactNode, useEffect } from "react";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import {
  Camera,
  Dumbbell,
  HelpCircle,
  Target,
  TrendingUp,
  Utensils,
} from "lucide-react";

import { SignUpForm } from "@/features/auth/forms/sign-up-form";
import { cn } from "@/lib/utils/cn";

const HERO_IMAGE_SRC = "/images/auth/signup-background.png";

export default function SignUpPage() {
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  const springConfig = { stiffness: 100, damping: 30 };
  const dx = useSpring(mouseX, springConfig);
  const dy = useSpring(mouseY, springConfig);

  const heroX = useTransform(dx, [-500, 500], [-20, 20]);
  const heroY = useTransform(dy, [-500, 500], [-20, 20]);
  const notifyX = useTransform(dx, [-500, 500], [30, -30]);
  const notifyY = useTransform(dy, [-500, 500], [30, -30]);

  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      mouseX.set(event.clientX - window.innerWidth / 2);
      mouseY.set(event.clientY - window.innerHeight / 2);
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [mouseX, mouseY]);

  return (
    <div className="relative flex min-h-screen flex-col overflow-hidden bg-background">
      <div className="noise-overlay" />

      <main className="flex flex-1 flex-col md:flex-row">
        <section className="relative flex min-h-[600px] w-full items-end overflow-hidden p-8 md:min-h-screen md:w-3/5 md:p-16">
          <div className="absolute inset-0 z-0">
            <img
              src={HERO_IMAGE_SRC}
              alt="Gym Interior"
              className="h-full w-full object-cover opacity-60"
            />
            <div className="absolute inset-0 bg-gradient-to-tr from-background via-background/90 to-transparent" />
          </div>

          <div className="absolute left-8 top-8 z-20 flex items-center justify-between md:left-16 md:right-16 md:top-12">
            <div className="text-3xl font-black italic tracking-tighter text-primary">
              FitFuel AI
            </div>
          </div>

          <button
            type="button"
            aria-label="Help"
            className="absolute right-8 top-8 z-20 inline-flex h-10 w-10 items-center justify-center rounded-full bg-primary text-on-primary shadow-[0_0_18px_rgba(78,222,163,0.24)] transition hover:scale-[1.03] md:right-16 md:top-12"
          >
            <HelpCircle className="h-5 w-5" />
          </button>

          <motion.div
            style={{ x: heroX, y: heroY }}
            className="relative z-10 w-full max-w-2xl"
          >
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
              className="mb-6 font-headline text-5xl font-extrabold leading-[0.9] tracking-tight text-white md:text-7xl"
            >
              Your AI fitness coach is{" "}
              <span className="italic text-primary">ready</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="mb-10 max-w-xl text-lg leading-relaxed text-on-surface-variant md:text-xl"
            >
              Get instant meal plans, photo-based calorie tracking with ResNet50 AI,
              progress analytics, and smart recommendations tailored to you.
            </motion.p>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <FeatureCard
                icon={<Target className="h-8 w-8 text-primary" />}
                title="Personalized Macro Targets"
                description="Our AI calculates your optimal protein, carb, and fat ratios based on your body metrics and fitness goals."
              />
              <FeatureCard
                icon={<Camera className="h-8 w-8 text-secondary" />}
                title="Smart Food Photo Estimator"
                description="Snap a photo of your meal and our ResNet50 vision model estimates calories and macros instantly."
              />
              <FeatureCard
                icon={<TrendingUp className="h-8 w-8 text-[#71a1ff]" />}
                title="Weekly AI Insights"
                description="Receive deep-dive analytics and personalized coaching tips based on your eating habits and progress."
              />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20, x: 20, rotate: 3 }}
            animate={{ opacity: 1, y: 0, x: 0, rotate: 3 }}
            style={{ x: notifyX, y: notifyY }}
            whileHover={{
              scale: 1.05,
              rotate: 0,
              boxShadow: "0 0 40px rgba(78,222,163,0.3)",
              borderColor: "rgba(78,222,163,0.5)",
            }}
            transition={{ duration: 0.4, delay: 0.6 }}
            className="absolute right-10 top-24 hidden w-72 cursor-pointer rounded-[2rem] border border-white/20 bg-white/10 p-4 shadow-2xl backdrop-blur-2xl transition-colors lg:block"
          >
            <div className="mb-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-primary p-1 shadow-lg shadow-primary/20">
                  <Utensils className="h-full w-full text-on-primary" />
                </div>
                <span className="text-[10px] font-bold uppercase tracking-widest text-white/60">
                  FitFuel AI
                </span>
              </div>
              <span className="text-[10px] font-medium text-white/40">now</span>
            </div>

            <div className="flex gap-3">
              <div className="flex-1">
                <h4 className="text-sm font-bold text-white">Meal Detected</h4>
                <p className="text-xs text-white/70">
                  Avocado Toast with Poached Egg detected. Approx. 340 kcal.
                </p>
              </div>
              <div className="h-12 w-12 overflow-hidden rounded-xl bg-surface-container-highest">
                <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-primary/30 to-secondary/20">
                  <Utensils className="h-5 w-5 text-primary" />
                </div>
              </div>
            </div>

            <div className="mt-4 space-y-2 rounded-2xl bg-black/20 p-3">
              <div className="flex justify-between text-[10px] font-bold text-primary">
                <span>Protein Goal</span>
                <span>65%</span>
              </div>
              <div className="h-1 w-full overflow-hidden rounded-full bg-white/10">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: "65%" }}
                  transition={{ duration: 1.5, delay: 1.2 }}
                  className="h-full bg-primary shadow-[0_0_8px_rgba(78,222,163,0.5)]"
                />
              </div>
            </div>
          </motion.div>
        </section>

        <section className="flex w-full flex-col justify-center bg-[rgba(12,19,34,0.94)] px-8 py-12 md:w-2/5 md:px-16">
          <div className="mx-auto w-full max-w-md">
            <div className="mb-12">
              <div className="text-3xl font-black italic tracking-tighter text-primary">
                FitFuel AI
              </div>
            </div>

            <div className="mb-8">
              <h2 className="mb-2 font-headline text-3xl font-bold text-white">
                Start your journey
              </h2>
              <p className="text-sm text-on-surface-variant">
                Create your account and get your personalized AI nutrition plan
              </p>
            </div>

            <SignUpForm />
          </div>
        </section>
      </main>

      <PageFooter />

      <style jsx global>{`
        .noise-overlay {
          position: fixed;
          inset: 0;
          opacity: 0.03;
          z-index: 50;
          pointer-events: none;
          background-image: url("https://grainy-gradients.vercel.app/noise.svg");
        }

        .shimmer-effect {
          position: relative;
          overflow: hidden;
        }

        .shimmer-effect::after {
          content: "";
          position: absolute;
          top: -50%;
          left: -50%;
          width: 200%;
          height: 200%;
          background: linear-gradient(
            to bottom right,
            rgba(255, 255, 255, 0) 0%,
            rgba(255, 255, 255, 0) 40%,
            rgba(255, 255, 255, 0.35) 50%,
            rgba(255, 255, 255, 0) 60%,
            rgba(255, 255, 255, 0) 100%
          );
          transform: rotate(45deg);
          animation: fitfuel-signup-shimmer 3s infinite;
        }

        @keyframes fitfuel-signup-shimmer {
          0% {
            transform: translateX(-150%) rotate(45deg);
          }
          100% {
            transform: translateX(150%) rotate(45deg);
          }
        }
      `}</style>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="h-32 [perspective:1000px]">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        whileHover={{ rotateY: 180 }}
        transition={{
          type: "spring",
          stiffness: 260,
          damping: 20,
        }}
        style={{ transformStyle: "preserve-3d" }}
        className="relative h-full w-full cursor-pointer"
      >
        <div
          className="absolute inset-0 flex flex-col gap-3 rounded-xl border border-outline-variant/15 bg-surface-container-low/40 p-4 backdrop-blur-md"
          style={{ backfaceVisibility: "hidden" }}
        >
          {icon}
          <span className="font-headline text-sm font-bold text-white">{title}</span>
        </div>

        <div
          className="absolute inset-0 flex items-center justify-center rounded-xl border border-primary/30 bg-surface-container-high p-4 text-center"
          style={{
            backfaceVisibility: "hidden",
            transform: "rotateY(180deg)",
          }}
        >
          <p className="text-[11px] leading-snug text-on-surface">{description}</p>
        </div>
      </motion.div>
    </div>
  );
}

function PageFooter() {
  return (
    <footer className="w-full border-t border-outline-variant/15 bg-background py-8">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-8 md:flex-row">
        <div className="text-sm font-bold text-primary">FitFuel AI</div>

        <div className="flex gap-6">
          <Link
            href="/sign-up#privacy"
            className="text-xs text-on-surface-variant transition-colors hover:text-on-surface"
          >
            Privacy Policy
          </Link>
          <Link
            href="/sign-up#terms"
            className="text-xs text-on-surface-variant transition-colors hover:text-on-surface"
          >
            Terms of Service
          </Link>
          <Link
            href="/sign-up#cookies"
            className="text-xs text-on-surface-variant transition-colors hover:text-on-surface"
          >
            Cookie Settings
          </Link>
        </div>

        <p className="text-xs text-on-surface-variant">
          © 2024 FitFuel AI. Kinetic Sanctuary Design.
        </p>
      </div>
    </footer>
  );
}