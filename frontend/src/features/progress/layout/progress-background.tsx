"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

export function ProgressBackground() {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      setMousePos({ x: event.clientX, y: event.clientY });
    };

    window.addEventListener("mousemove", handleMouseMove);

    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
      <motion.div
        animate={{
          x: mousePos.x - 180,
          y: mousePos.y - 180,
        }}
        transition={{ type: "spring", damping: 28, stiffness: 140, mass: 0.7 }}
        className="absolute h-[360px] w-[360px] rounded-full bg-primary/10 blur-[90px]"
      />

      <div className="absolute left-[-10%] top-[-10%] h-[42%] w-[42%] rounded-full bg-primary/5 blur-[120px]" />
      <div className="absolute bottom-[-10%] right-[-10%] h-[36%] w-[36%] rounded-full bg-secondary/5 blur-[120px]" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(78,222,163,0.08),transparent_40%)]" />
      <div className="absolute inset-0 bg-[linear-gradient(to_bottom,rgba(12,19,34,0.2),rgba(12,19,34,0.9))]" />
    </div>
  );
}