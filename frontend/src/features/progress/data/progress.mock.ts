export type TrendPoint = {
  label: string;
  value: number;
};

export type MetricRow = {
  date: string;
  weight: number;
  bodyFat: number;
  status: "Decrease" | "Stable" | "Increase";
  trend: "down" | "flat" | "up";
};

export const weightTrendData: TrendPoint[] = Array.from({ length: 32 }, (_, index) => {
  const baseWeight = 86.5;
  const targetWeight = 83.5;
  const progress = index / 31;
  const trend = baseWeight - (baseWeight - targetWeight) * progress;
  const fluctuation = Math.sin(index * 0.5) * 0.2;

  return {
    label:
      index === 0 ? "Oct 01" : index === 15 ? "Oct 15" : index === 31 ? "Today" : `${index}`,
    value: Number((trend + fluctuation).toFixed(1)),
  };
});

export const calorieTrendData = [
  { day: "Mon", target: 2450, actual: 2310 },
  { day: "Tue", target: 2450, actual: 2385 },
  { day: "Wed", target: 2450, actual: 2495 },
  { day: "Thu", target: 2450, actual: 2410 },
  { day: "Fri", target: 2450, actual: 2360 },
  { day: "Sat", target: 2450, actual: 2520 },
  { day: "Sun", target: 2450, actual: 2430 },
];

export const hydrationTrendData = [
  { day: "Mon", liters: 2.4 },
  { day: "Tue", liters: 2.7 },
  { day: "Wed", liters: 2.1 },
  { day: "Thu", liters: 3.0 },
  { day: "Fri", liters: 2.8 },
  { day: "Sat", liters: 3.2 },
  { day: "Sun", liters: 2.6 },
];

export const stepsTrendData = [
  { day: "Mon", steps: 7800 },
  { day: "Tue", steps: 9200 },
  { day: "Wed", steps: 10800 },
  { day: "Thu", steps: 9600 },
  { day: "Fri", steps: 11300 },
  { day: "Sat", steps: 12600 },
  { day: "Sun", steps: 8450 },
];

export const recentMetrics: MetricRow[] = [
  {
    date: "Oct 20",
    weight: 84.2,
    bodyFat: 18.4,
    status: "Decrease",
    trend: "down",
  },
  {
    date: "Oct 18",
    weight: 84.5,
    bodyFat: 18.7,
    status: "Decrease",
    trend: "down",
  },
  {
    date: "Oct 16",
    weight: 84.6,
    bodyFat: 18.7,
    status: "Stable",
    trend: "flat",
  },
  {
    date: "Oct 14",
    weight: 84.9,
    bodyFat: 19.1,
    status: "Increase",
    trend: "up",
  },
];

export const macroRatioData = [
  { label: "Protein", current: 152, target: 170, color: "#4edea3" },
  { label: "Carbs", current: 224, target: 260, color: "#ffb95f" },
  { label: "Fats", current: 61, target: 72, color: "#90a8ff" },
];

export const waterSchedule = [
  { time: "07:00", label: "Wake-up glass", amount: "350ml", done: true },
  { time: "10:00", label: "Mid-morning", amount: "500ml", done: true },
  { time: "13:00", label: "Lunch hydration", amount: "600ml", done: false },
  { time: "16:00", label: "Training prep", amount: "450ml", done: false },
  { time: "20:00", label: "Evening top-up", amount: "500ml", done: false },
];

export const stepSessions = [
  { label: "Morning walk", value: 3200, duration: "26 min" },
  { label: "Campus commute", value: 2800, duration: "21 min" },
  { label: "Gym cooldown", value: 1900, duration: "14 min" },
  { label: "Evening walk", value: 4600, duration: "34 min" },
];