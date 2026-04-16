"use client";

import { cn } from "@/lib/utils/cn";

type SliderProps = {
  value: number[];
  onValueChange: (value: number[]) => void;
  min: number;
  max: number;
  step?: number;
  className?: string;
};

export function Slider({
  value,
  onValueChange,
  min,
  max,
  step = 1,
  className,
}: Readonly<SliderProps>) {
  const currentValue = value[0] ?? min;
  const percentage = ((currentValue - min) / (max - min)) * 100;

  return (
    <div className={cn("relative flex items-center", className)}>
      <div className="absolute inset-x-0 h-2 rounded-full bg-surface-container-highest/70" />
      <div
        className="absolute left-0 h-2 rounded-full bg-primary shadow-[0_0_15px_rgba(78,222,163,0.35)]"
        style={{ width: `${percentage}%` }}
      />
      <input
        type="range"
        value={currentValue}
        min={min}
        max={max}
        step={step}
        onChange={(event) => onValueChange([Number(event.target.value)])}
        className={cn(
          "relative z-10 h-8 w-full appearance-none bg-transparent",
          "[&::-webkit-slider-runnable-track]:h-2",
          "[&::-webkit-slider-runnable-track]:rounded-full",
          "[&::-webkit-slider-runnable-track]:bg-transparent",
          "[&::-webkit-slider-thumb]:-mt-2.5",
          "[&::-webkit-slider-thumb]:h-7",
          "[&::-webkit-slider-thumb]:w-7",
          "[&::-webkit-slider-thumb]:appearance-none",
          "[&::-webkit-slider-thumb]:rounded-full",
          "[&::-webkit-slider-thumb]:border-4",
          "[&::-webkit-slider-thumb]:border-background",
          "[&::-webkit-slider-thumb]:bg-primary",
          "[&::-webkit-slider-thumb]:shadow-[0_0_20px_rgba(78,222,163,0.45)]",
          "[&::-moz-range-track]:h-2",
          "[&::-moz-range-track]:rounded-full",
          "[&::-moz-range-track]:bg-transparent",
          "[&::-moz-range-thumb]:h-7",
          "[&::-moz-range-thumb]:w-7",
          "[&::-moz-range-thumb]:rounded-full",
          "[&::-moz-range-thumb]:border-4",
          "[&::-moz-range-thumb]:border-background",
          "[&::-moz-range-thumb]:bg-primary",
          "[&::-moz-range-thumb]:shadow-[0_0_20px_rgba(78,222,163,0.45)]"
        )}
      />
    </div>
  );
}