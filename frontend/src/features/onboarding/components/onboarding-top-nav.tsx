"use client";

import { motion } from "framer-motion";
import { User } from "lucide-react";

export function OnboardingTopNav() {
  return (
    <nav className="fixed top-0 z-50 flex w-full items-center justify-between border-b border-white/5 bg-slate-950/60 px-6 py-4 font-headline text-white shadow-2xl shadow-primary/5 backdrop-blur-3xl">
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="cursor-default text-2xl font-black tracking-tighter text-primary"
      >
        FitFuel AI
      </motion.div>

      <div className="flex items-center gap-4">
        <motion.button
          whileHover={{ scale: 1.1, color: "#4edea3" }}
          whileTap={{ scale: 0.9 }}
          className="text-on-surface-variant transition-colors"
          type="button"
          aria-label="Profile"
        >
          <User className="h-6 w-6" />
        </motion.button>
      </div>
    </nav>
  );
}