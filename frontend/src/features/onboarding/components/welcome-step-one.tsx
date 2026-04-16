"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import {
  Activity,
  ArrowRight,
  Brain,
  Leaf,
  ShieldCheck,
  Target,
  TrendingUp,
  Zap,
} from "lucide-react";
import {
  motion,
  useMotionValue,
  useSpring,
  useTransform,
} from "framer-motion";

import { KineticBackground } from "@/features/onboarding/components/kinetic-background";
import { OnboardingSideNav } from "@/features/onboarding/components/onboarding-side-nav";
import { OnboardingTopNav } from "@/features/onboarding/components/onboarding-top-nav";
import { cn } from "@/lib/utils/cn";

const HERO_IMAGE_URL =
  "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=2070&auto=format&fit=crop";

function TiltCard({
  children,
  className,
}: Readonly<{
  children: ReactNode;
  className?: string;
}>) {
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const mouseXSpring = useSpring(x);
  const mouseYSpring = useSpring(y);

  const rotateX = useTransform(mouseYSpring, [-0.5, 0.5], ["10deg", "-10deg"]);
  const rotateY = useTransform(mouseXSpring, [-0.5, 0.5], ["-10deg", "10deg"]);

  const handleMouseMove = (event: React.MouseEvent<HTMLDivElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;
    const xPct = mouseX / width - 0.5;
    const yPct = mouseY / height - 0.5;

    x.set(xPct);
    y.set(yPct);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  return (
    <motion.div
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        rotateY,
        rotateX,
        transformStyle: "preserve-3d",
      }}
      className={cn("relative", className)}
    >
      <div style={{ transform: "translateZ(50px)", transformStyle: "preserve-3d" }}>
        {children}
      </div>
    </motion.div>
  );
}

export function WelcomeStepOne() {
  const features = [
    {
      icon: Brain,
      title: "Neural Nutrition",
      desc: "Sophisticated algorithms that learn your body's specific response to over 500,000 unique food combinations.",
    },
    {
      icon: Target,
      title: "Precision Goals",
      desc: "Goal-based guidance tuned to your targets, habits, and daily energy balance.",
    },
    {
      icon: Leaf,
      title: "Adaptive Planning",
      desc: "Meal recommendations that adjust to your lifestyle, preferences, and long-term consistency.",
    },
  ] as const;

  return (
    <div className="min-h-screen overflow-x-hidden bg-background text-on-background font-sans selection:bg-primary/30">
      <OnboardingTopNav />

      <div className="flex min-h-screen">
        <OnboardingSideNav progressStep={1} activeStepId="profile" />

        <main className="flex-1">
          <div className="relative flex-1 overflow-hidden px-6 pb-12 pt-24 md:px-12 lg:px-20">
            <KineticBackground />

            <section className="mx-auto mt-12 flex max-w-6xl flex-col items-center gap-12 text-center lg:mt-24 lg:flex-row lg:gap-20 lg:text-left">
              <motion.div
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                className="z-10 flex-1"
              >
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="mb-8 inline-flex items-center gap-4 rounded-full border border-white/5 bg-surface-container-low/50 px-4 py-2 shadow-inner backdrop-blur-md lg:mb-12"
                >
                  <div className="flex gap-1.5">
                    <motion.div
                      animate={{ opacity: [0.4, 1, 0.4] }}
                      transition={{ duration: 2, repeat: Infinity }}
                      className="h-1.5 w-8 rounded-full bg-primary"
                    />
                    <div className="h-1.5 w-8 rounded-full bg-surface-container-highest" />
                    <div className="h-1.5 w-8 rounded-full bg-surface-container-highest" />
                    <div className="h-1.5 w-8 rounded-full bg-surface-container-highest" />
                  </div>
                  <span className="text-xs font-bold uppercase tracking-widest text-primary">
                    Step 1 of 4
                  </span>
                </motion.div>

                <h1 className="mb-6 font-headline text-5xl font-extrabold leading-[1.05] tracking-tight text-white md:text-6xl lg:text-8xl">
                  Let&apos;s build your{" "}
                  <span className="text-gradient animate-pulse">best self</span>
                </h1>

                <p className="mb-10 max-w-xl text-lg leading-relaxed text-on-surface-variant md:text-xl">
                  Harness the power of AI-driven nutrition. Tailored meal plans,
                  kinetic tracking, and biological insights designed specifically
                  for your performance goals.
                </p>

                <div className="flex flex-col items-center gap-6 sm:flex-row">
                  <Link
                    href="/personal-details"
                    className="group flex w-full items-center justify-center gap-3 rounded-full bg-primary px-10 py-5 text-lg font-bold text-on-primary shadow-[0_0_20px_rgba(78,222,163,0.2)] transition-all duration-300 hover:scale-[1.05] hover:shadow-[0_0_40px_rgba(78,222,163,0.4)] sm:w-auto"
                  >
                    Get Started
                    <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
                  </Link>

                  <Link
                    href="/goals"
                    className="group flex items-center gap-2 px-8 py-5 font-bold text-on-surface transition-colors hover:text-primary"
                  >
                    Explore Plans
                    <motion.span
                      animate={{ x: [0, 5, 0] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    >
                      →
                    </motion.span>
                  </Link>
                </div>

                <div className="mt-16 flex flex-wrap gap-8 pt-12 opacity-60">
                  <div className="group flex cursor-default items-center gap-3">
                    <ShieldCheck className="h-5 w-5 text-primary transition-transform group-hover:scale-110" />
                    <span className="text-sm font-bold uppercase tracking-wider">
                      AI Validated
                    </span>
                  </div>

                  <div className="group flex cursor-default items-center gap-3">
                    <Activity className="h-5 w-5 text-primary transition-transform group-hover:scale-110" />
                    <span className="text-sm font-bold uppercase tracking-wider">
                      Secure Data
                    </span>
                  </div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{
                  duration: 1,
                  ease: [0.16, 1, 0.3, 1],
                  delay: 0.2,
                }}
                className="relative w-full max-w-lg flex-1 [perspective:1000px] lg:max-w-none"
              >
                <TiltCard>
                  <div className="relative z-10 aspect-square w-full overflow-hidden rounded-xl border border-white/10 shadow-2xl md:aspect-[4/5]">
                    <img
                      alt="Performance fitness"
                      className="h-full w-full object-cover brightness-75 grayscale-[20%] transition-transform duration-700 hover:scale-110"
                      src={HERO_IMAGE_URL}
                      referrerPolicy="no-referrer"
                    />

                    <div
                      className="kinetic-glass absolute bottom-8 left-8 right-8 rounded-lg border border-white/10 p-6 shadow-2xl"
                      style={{ transform: "translateZ(80px)" }}
                    >
                      <div className="mb-4 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="h-2 w-2 animate-pulse rounded-full bg-primary shadow-[0_0_10px_#4edea3]" />
                          <span className="text-xs font-bold uppercase tracking-widest text-primary">
                            AI Metabolism Engine
                          </span>
                        </div>
                        <span className="font-mono text-xs text-on-surface/60">
                          LIVE_UPDATE_01
                        </span>
                      </div>

                      <div className="space-y-4">
                        <div className="relative h-2 w-full overflow-hidden rounded-full bg-surface-container-highest">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: "88%" }}
                            transition={{ duration: 2, delay: 1, ease: "circOut" }}
                            className="relative h-full bg-primary"
                          >
                            <motion.div
                              animate={{ x: ["0%", "100%"] }}
                              transition={{
                                duration: 1.5,
                                repeat: Infinity,
                                ease: "linear",
                              }}
                              className="absolute bottom-0 top-0 w-20 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                            />
                          </motion.div>
                        </div>

                        <div className="flex justify-between text-lg font-bold italic text-white">
                          <span>Protein Optimization</span>
                          <motion.span
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 2.5 }}
                          >
                            88%
                          </motion.span>
                        </div>
                      </div>
                    </div>
                  </div>
                </TiltCard>

                <div className="absolute -right-20 -top-20 h-80 w-80 animate-pulse rounded-full bg-primary/20 blur-[120px]" />
                <div
                  className="absolute -bottom-20 -left-20 h-80 w-80 animate-pulse rounded-full bg-secondary/10 blur-[120px]"
                  style={{ animationDelay: "1s" }}
                />

                <motion.div
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.8, type: "spring", stiffness: 100 }}
                  className="absolute -right-4 -top-10 z-20 hidden rounded-lg border border-white/10 bg-surface-container-highest/80 p-4 shadow-xl backdrop-blur-md md:block"
                  style={{ transform: "translateZ(100px)" }}
                >
                  <div className="flex items-center gap-3">
                    <div className="relative rounded-full bg-primary/20 p-2">
                      <motion.div
                        animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
                        transition={{ duration: 2, repeat: Infinity }}
                        className="absolute inset-0 rounded-full bg-primary"
                      />
                      <Zap className="relative z-10 h-5 w-5 fill-primary text-primary" />
                    </div>

                    <div>
                      <div className="text-xs font-bold uppercase tracking-tighter text-on-surface-variant">
                        Peak Energy
                      </div>
                      <div className="text-xl font-bold tracking-tight text-white">
                        2,450 kcal
                      </div>
                    </div>
                  </div>
                </motion.div>
              </motion.div>
            </section>

            <section className="relative z-10 mx-auto mt-32 grid max-w-6xl grid-cols-1 gap-8 md:grid-cols-3">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.15, duration: 0.6 }}
                  whileHover={{
                    y: -10,
                    backgroundColor: "rgba(35, 42, 58, 0.8)",
                  }}
                  className="rounded-lg border border-white/5 bg-surface-container-low/50 p-8 transition-all backdrop-blur-sm"
                >
                  <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 transition-colors group-hover:bg-primary/20">
                    <feature.icon className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="mb-2 text-xl font-bold text-white">
                    {feature.title}
                  </h3>
                  <p className="text-sm leading-relaxed text-on-surface-variant">
                    {feature.desc}
                  </p>
                </motion.div>
              ))}
            </section>
          </div>
        </main>
      </div>

      <style jsx global>{`
        .text-gradient {
          background: linear-gradient(90deg, #4edea3 0%, #6ffbbe 55%, #ffb95f 100%);
          -webkit-background-clip: text;
          background-clip: text;
          color: transparent;
        }

        .kinetic-glass {
          background: linear-gradient(
            135deg,
            rgba(16, 185, 129, 0.1) 0%,
            rgba(20, 27, 43, 0.4) 100%
          );
          backdrop-filter: blur(24px);
          -webkit-backdrop-filter: blur(24px);
        }
      `}</style>
    </div>
  );
}