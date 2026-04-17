"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { motion, type Variants } from "framer-motion";
import {
  Bolt,
  CheckCircle2,
  Droplets,
  Dumbbell,
  Info,
  Leaf,
  Send,
  Utensils,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { useAssistantPageQuery } from "@/features/assistant/hooks/use-assistant-page-query";
import { useSendChatMessageMutation } from "@/features/assistant/hooks/use-send-chat-message-mutation";
import type {
  ChatMessageResponse,
  ProgressSnapshotResponse,
  UserGoalResponse,
} from "@/features/assistant/types/assistant.types";

const suggestions = [
  "Meal swap",
  "Recipe ideas",
  "Macro explanation",
  "Grocery help",
] as const;

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.12,
    },
  },
};

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.45, ease: "easeOut" },
  },
};

function TypingDots() {
  return (
    <div className="w-fit rounded-xl rounded-tl-none border border-white/5 bg-surface-container-high/40 px-4 py-3 backdrop-blur-xl">
      <div className="flex gap-1.5">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            animate={{ y: [0, -4, 0], opacity: [0.4, 1, 0.4] }}
            transition={{
              duration: 0.8,
              repeat: Infinity,
              delay: i * 0.15,
              ease: "easeInOut",
            }}
            className="h-2 w-2 rounded-full bg-primary shadow-[0_0_8px_rgba(78,222,163,0.3)]"
          />
        ))}
      </div>
    </div>
  );
}

function buildChartData(
  currentGoal: UserGoalResponse | null,
  latestSnapshot: ProgressSnapshotResponse | null
) {
  if (!currentGoal && !latestSnapshot) {
    return [];
  }

  const targetCalories =
    latestSnapshot?.target_calories ?? currentGoal?.target_calories ?? 0;
  const targetProtein =
    latestSnapshot?.target_protein_g ?? currentGoal?.target_protein_g ?? 0;
  const targetCarbs =
    latestSnapshot?.target_carbs_g ?? currentGoal?.target_carbs_g ?? 0;
  const targetFat =
    latestSnapshot?.target_fat_g ?? currentGoal?.target_fat_g ?? 0;

  const consumedCalories = latestSnapshot?.consumed_calories ?? 0;
  const consumedProtein = latestSnapshot?.consumed_protein_g ?? 0;
  const consumedCarbs = latestSnapshot?.consumed_carbs_g ?? 0;
  const consumedFat = latestSnapshot?.consumed_fat_g ?? 0;

  return [
    {
      name: "Calories",
      target: Math.round(targetCalories),
      actual: Math.round(consumedCalories),
      unit: "kcal",
    },
    {
      name: "Protein",
      target: Math.round(targetProtein),
      actual: Math.round(consumedProtein),
      unit: "g",
    },
    {
      name: "Carbs",
      target: Math.round(targetCarbs),
      actual: Math.round(consumedCarbs),
      unit: "g",
    },
    {
      name: "Fats",
      target: Math.round(targetFat),
      actual: Math.round(consumedFat),
      unit: "g",
    },
  ];
}

function buildInsights(
  currentGoal: UserGoalResponse | null,
  latestSnapshot: ProgressSnapshotResponse | null
) {
  if (!currentGoal && !latestSnapshot) {
    return [
      "Ask for a meal swap based on your goals.",
      "Request macro explanations or grocery help.",
      "Use the assistant to refine today’s meal choices.",
    ];
  }

  const targetCalories =
    latestSnapshot?.target_calories ?? currentGoal?.target_calories ?? 0;
  const consumedCalories = latestSnapshot?.consumed_calories ?? 0;
  const remainingCalories = Math.max(targetCalories - consumedCalories, 0);

  const targetProtein =
    latestSnapshot?.target_protein_g ?? currentGoal?.target_protein_g ?? 0;
  const consumedProtein = latestSnapshot?.consumed_protein_g ?? 0;
  const remainingProtein = Math.max(targetProtein - consumedProtein, 0);

  const adherence = latestSnapshot?.overall_adherence_score ?? 0;

  return [
    `${remainingCalories.toLocaleString()} kcal remaining today.`,
    `${Math.round(remainingProtein)}g protein still available before target.`,
    adherence > 0
      ? `Current adherence score: ${Math.round(adherence)}%.`
      : "No adherence snapshot recorded yet for today.",
  ];
}

function normalizeIntent(value: string | null | undefined): string {
  return (value ?? "").trim().toLowerCase();
}

function isSwapOrComparisonIntent(intent: string): boolean {
  return [
    "meal_swap",
    "food_swap",
    "swap_food",
    "swap_item",
    "compare_meals",
    "meal_comparison",
    "compare_foods",
  ].includes(intent);
}

function isSwapOrComparisonPrompt(content: string): boolean {
  const text = content.toLowerCase();

  return [
    "swap",
    "replace",
    "instead of",
    "alternative to",
    "compare",
    "comparison",
    "vs ",
    " vs ",
    "versus",
    "better than",
  ].some((keyword) => text.includes(keyword));
}

function formatAssistantText(content: string) {
  const normalized = content
    .replace(/\r\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();

  const parts = normalized
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean);

  return parts.map((line, index) => {
    const html = line
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>");

    const isBullet =
      line.startsWith("- ") ||
      line.startsWith("• ") ||
      /^\d+\.\s/.test(line);

    if (isBullet) {
      const cleaned = html.replace(/^(-|•)\s+/, "").replace(/^\d+\.\s+/, "");

      return (
        <div
          key={`${index}-${cleaned}`}
          className="flex items-start gap-3"
        >
          <div className="mt-2 h-1.5 w-1.5 rounded-full bg-primary" />
          <p
            className="text-lg font-medium leading-relaxed text-on-surface"
            dangerouslySetInnerHTML={{ __html: cleaned }}
          />
        </div>
      );
    }

    return (
      <p
        key={`${index}-${html}`}
        className="text-lg font-medium leading-relaxed text-on-surface"
        dangerouslySetInnerHTML={{ __html: html }}
      />
    );
  });
}

function CustomTooltip({
  active,
  payload,
  label,
}: Readonly<{
  active?: boolean;
  payload?: Array<{ value: number; payload: { unit: string } }>;
  label?: string;
}>) {
  if (!active || !payload || payload.length < 2 || !label) {
    return null;
  }

  return (
    <div className="rounded-xl border border-white/10 bg-surface-container-highest/90 p-4 shadow-2xl backdrop-blur-xl">
      <p className="mb-2 font-headline font-bold text-on-surface">{label}</p>
      <div className="space-y-1">
        <p className="flex items-center justify-between gap-4 text-sm font-medium">
          <span className="text-slate-400">Target:</span>
          <span className="font-bold text-primary">
            {payload[0].value}
            {payload[0].payload.unit}
          </span>
        </p>
        <p className="flex items-center justify-between gap-4 text-sm font-medium">
          <span className="text-primary/70">Actual:</span>
          <span className="font-bold text-secondary">
            {payload[1].value}
            {payload[1].payload.unit}
          </span>
        </p>
      </div>
    </div>
  );
}

function StructuredInsightsPanel({
  chartData,
  insights,
}: Readonly<{
  chartData: Array<{
    name: string;
    target: number;
    actual: number;
    unit: string;
  }>;
  insights: string[];
}>) {
  if (chartData.length === 0) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      className="mx-8 mb-4 rounded-2xl border border-white/5 bg-surface-container-low/60 p-6 shadow-2xl backdrop-blur-md"
    >
      <div className="mb-6 flex items-center justify-between">
        <div className="space-y-1">
          <h4 className="font-headline text-lg font-bold text-on-surface">
            Nutrition Context
          </h4>
          <p className="text-xs font-bold uppercase tracking-widest text-slate-500">
            Target vs actual today
          </p>
        </div>

        <div className="flex gap-4">
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-primary" />
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Target
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-secondary" />
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Actual
            </span>
          </div>
        </div>
      </div>

      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 0, bottom: 0 }}
            barGap={12}
          >
            <CartesianGrid
              vertical={false}
              stroke="#2e3545"
              strokeDasharray="3 3"
            />
            <XAxis
              dataKey="name"
              axisLine={false}
              tickLine={false}
              tick={{
                fill: "#86948a",
                fontSize: 12,
                fontWeight: 700,
              }}
              dy={10}
            />
            <YAxis hide />
            <Tooltip
              content={<CustomTooltip />}
              cursor={{ fill: "rgba(255,255,255,0.03)" }}
            />
            <Bar
              dataKey="target"
              fill="#4edea3"
              radius={[6, 6, 0, 0]}
              animationDuration={1200}
            />
            <Bar
              dataKey="actual"
              fill="#ffb95f"
              radius={[6, 6, 0, 0]}
              animationDuration={1200}
              animationDelay={250}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {insights.length > 0 ? (
        <div className="mt-5 space-y-3">
          {insights.map((insight, idx) => (
            <motion.div
              key={insight}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.08 }}
              className="flex items-center gap-3"
            >
              <CheckCircle2 className="h-5 w-5 text-primary" />
              <span className="font-medium text-on-surface-variant">
                {insight}
              </span>
            </motion.div>
          ))}
        </div>
      ) : null}
    </motion.div>
  );
}

function DailyContextPanel({
  currentGoal,
  latestSnapshot,
}: Readonly<{
  currentGoal: UserGoalResponse | null;
  latestSnapshot: ProgressSnapshotResponse | null;
}>) {
  const targetCalories =
    latestSnapshot?.target_calories ?? currentGoal?.target_calories ?? 0;
  const consumedCalories = latestSnapshot?.consumed_calories ?? 0;
  const remainingCalories = Math.max(targetCalories - consumedCalories, 0);

  const circleProgress =
    targetCalories > 0 ? Math.min(consumedCalories / targetCalories, 1) : 0;

  const macros = [
    {
      label: "Protein",
      value: latestSnapshot?.consumed_protein_g ?? 0,
      target:
        latestSnapshot?.target_protein_g ?? currentGoal?.target_protein_g ?? 0,
      icon: <Dumbbell className="h-4 w-4" />,
      color: "text-primary",
      bg: "bg-primary",
    },
    {
      label: "Carbs",
      value: latestSnapshot?.consumed_carbs_g ?? 0,
      target:
        latestSnapshot?.target_carbs_g ?? currentGoal?.target_carbs_g ?? 0,
      icon: <Utensils className="h-4 w-4" />,
      color: "text-secondary",
      bg: "bg-secondary",
    },
    {
      label: "Fats",
      value: latestSnapshot?.consumed_fat_g ?? 0,
      target: latestSnapshot?.target_fat_g ?? currentGoal?.target_fat_g ?? 0,
      icon: <Droplets className="h-4 w-4" />,
      color: "text-tertiary",
      bg: "bg-tertiary",
    },
  ];

  const circumference = 2 * Math.PI * 80;
  const offset = circumference - circumference * circleProgress;

  return (
    <aside className="flex h-full w-full flex-shrink-0 flex-col space-y-8 border-t border-white/[0.03] px-6 py-8 shadow-[-20px_0_40px_rgba(0,0,0,0.2)] backdrop-blur-2xl lg:w-80 lg:border-l lg:border-t-0 lg:bg-[#141b2b]/80">
      <div className="relative space-y-1">
        <div className="absolute -left-6 top-0 h-full w-1 rounded-full bg-primary/40 blur-sm" />
        <h2 className="font-headline text-2xl font-extrabold tracking-tight text-on-surface">
          Daily Context
        </h2>
        <p className="text-sm font-bold text-slate-500">
          Target: {targetCalories.toLocaleString()} kcal
        </p>
      </div>

      <div className="group relative flex items-center justify-center py-4">
        <div className="absolute inset-0 rounded-full bg-primary/5 blur-3xl transition-colors group-hover:bg-primary/10" />
        <svg className="relative h-48 w-48 -rotate-90 transition-transform duration-500 group-hover:scale-105">
          <circle
            className="text-surface-container-highest"
            cx="96"
            cy="96"
            fill="transparent"
            r="80"
            stroke="currentColor"
            strokeWidth="12"
          />
          <motion.circle
            className="text-primary"
            cx="96"
            cy="96"
            fill="transparent"
            r="80"
            stroke="currentColor"
            strokeWidth="12"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.1, ease: "easeOut" }}
          />
        </svg>

        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-headline text-4xl font-extrabold text-on-surface transition-colors group-hover:text-primary">
            {consumedCalories.toLocaleString()}
          </span>
          <span className="text-xs font-bold uppercase tracking-widest text-slate-500">
            Left: {remainingCalories.toLocaleString()}
          </span>
        </div>
      </div>

      <div className="space-y-6">
        {macros.map((macro) => {
          const target = Math.max(macro.target, 1);
          const pct = Math.min(macro.value / target, 1) * 100;

          return (
            <div
              key={macro.label}
              className="group/item cursor-default space-y-2"
            >
              <div className="flex items-end justify-between">
                <div
                  className={`flex items-center gap-2 transition-transform group-hover/item:scale-105 ${macro.color}`}
                >
                  {macro.icon}
                  <span className="font-body text-xs font-bold uppercase tracking-wider">
                    {macro.label}
                  </span>
                </div>
                <span className="font-headline text-sm font-bold text-on-surface">
                  {Math.round(macro.value)}g / {Math.round(macro.target)}g
                </span>
              </div>

              <div className="relative h-2 overflow-hidden rounded-full bg-surface-container-highest">
                <div
                  className={`relative z-10 h-full ${macro.bg}`}
                  style={{ width: `${pct}%` }}
                >
                  <div className="absolute inset-0 animate-drift bg-white/20 opacity-0 transition-opacity group-hover/item:opacity-100" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <button className="mt-auto w-full rounded-full border border-white/5 bg-surface-container-highest/50 py-4 font-headline font-extrabold text-on-surface shadow-lg transition-all duration-150 hover:border-white/10 hover:bg-surface-bright active:scale-95">
        Adjust Goals
      </button>
    </aside>
  );
}

export function AssistantScreen({
  accessToken,
}: Readonly<{
  accessToken: string;
}>) {
  const pageQuery = useAssistantPageQuery(accessToken);
  const sendMutation = useSendChatMessageMutation();

  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messagesOverride, setMessagesOverride] = useState<ChatMessageResponse[] | null>(null);
  const [inputValue, setInputValue] = useState("");
  const [pendingUserContent, setPendingUserContent] = useState<string | null>(null);

  const scrollRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!pageQuery.data?.latestSessionDetail) {
      return;
    }

    if (!activeSessionId) {
      setActiveSessionId(pageQuery.data.latestSessionDetail.id);
      setMessagesOverride(pageQuery.data.latestSessionDetail.messages);
      return;
    }

    if (pageQuery.data.latestSessionDetail.id === activeSessionId) {
      setMessagesOverride(pageQuery.data.latestSessionDetail.messages);
    }
  }, [activeSessionId, pageQuery.data?.latestSessionDetail]);

  useEffect(() => {
    if (!scrollRef.current) {
      return;
    }

    scrollRef.current.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messagesOverride, pendingUserContent, sendMutation.isPending]);

  const currentGoal = pageQuery.data?.currentGoal ?? null;
  const latestSnapshot = pageQuery.data?.latestSnapshot ?? null;

  const chartData = useMemo(
    () => buildChartData(currentGoal, latestSnapshot),
    [currentGoal, latestSnapshot]
  );

  const insights = useMemo(
    () => buildInsights(currentGoal, latestSnapshot),
    [currentGoal, latestSnapshot]
  );

  const messages = messagesOverride ?? pageQuery.data?.latestSessionDetail?.messages ?? [];

  const latestUserMessage =
    [...messages].reverse().find((message) => message.role === "user") ?? null;

  const latestAssistantMessage =
    [...messages].reverse().find((message) => message.role === "assistant") ?? null;

  const latestIntent = normalizeIntent(
    latestUserMessage?.detected_intent ?? latestAssistantMessage?.detected_intent
  );

  const latestPromptForDecision =
    pendingUserContent ?? latestUserMessage?.content ?? "";

  const shouldShowStructuredInsights =
    chartData.length > 0 &&
    (isSwapOrComparisonIntent(latestIntent) ||
      isSwapOrComparisonPrompt(latestPromptForDecision));

  const canSend = inputValue.trim().length > 0 && !sendMutation.isPending;

  const handleSend = (content: string) => {
    const trimmed = content.trim();

    if (!trimmed) {
      return;
    }

    setPendingUserContent(trimmed);
    setInputValue("");

    sendMutation.mutate(
      {
        accessToken,
        sessionId: activeSessionId,
        content: trimmed,
      },
      {
        onSuccess: (result) => {
          setActiveSessionId(result.sessionId);
          setMessagesOverride((current) => [
            ...(current ?? messages),
            result.turn.user_message,
            result.turn.assistant_message,
          ]);
          setPendingUserContent(null);
        },
        onError: () => {
          setInputValue(trimmed);
          setPendingUserContent(null);
        },
      }
    );
  };

  if (pageQuery.isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background">
        <LoadingState
          label="Loading your AI meal assistant..."
          className="text-primary"
        />
      </main>
    );
  }

  if (pageQuery.isError) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background px-6">
        <ErrorState message={pageQuery.error.message} />
      </main>
    );
  }

  return (
    <div className="relative min-h-[calc(100vh-5rem)] overflow-hidden bg-background text-on-surface">
      <div className="fixed left-0 top-0 -z-50 h-full w-full overflow-hidden bg-[#0c1322]">
        <div className="absolute inset-0 bg-grain opacity-[0.03] mix-blend-overlay" />
        <div className="absolute right-[-5%] top-[-10%] h-[70%] w-[60%] animate-drift overflow-hidden rounded-full bg-primary/20 blur-[140px] mix-blend-screen" />
        <div className="absolute bottom-[-15%] left-[-10%] h-[60%] w-[50%] animate-drift rounded-full bg-secondary/15 blur-[140px] mix-blend-screen [animation-delay:-5s]" />
        <div className="absolute left-[30%] top-[20%] h-[40%] w-[30%] animate-drift rounded-full bg-tertiary/10 blur-[120px] [animation-delay:-10s]" />
        <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-background/50" />
      </div>

      <main className="relative z-10 flex min-h-[calc(100vh-5rem)] flex-col overflow-hidden lg:h-[calc(100vh-5rem)] lg:flex-row">
        <section className="relative flex flex-grow flex-col">
          <div
            ref={scrollRef}
            className="mask-scroll-y no-scrollbar flex-grow overflow-y-auto px-8 py-10"
          >
            <div className="space-y-12">
              {messages.length === 0 && !pendingUserContent ? (
                <motion.div
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.45 }}
                  className="space-y-6"
                >
                  <div className="max-w-[78%] rounded-xl rounded-tl-none border border-white/5 bg-surface-container-high/40 px-6 py-4 shadow-2xl backdrop-blur-2xl">
                    <p className="text-lg font-medium leading-relaxed text-on-surface">
                      Ask me for meal swaps, recipe ideas, macro explanations, or
                      grocery guidance based on your current nutrition targets.
                    </p>
                  </div>

                  <div className="flex flex-wrap gap-3">
                    {suggestions.map((suggestion) => (
                      <motion.button
                        key={suggestion}
                        whileHover={{ scale: 1.05, y: -2 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setInputValue(suggestion)}
                        className="rounded-full border border-transparent bg-surface-container-highest/80 px-5 py-2.5 text-sm font-bold text-on-surface shadow-lg backdrop-blur-md transition-all hover:border-white/10 hover:bg-surface-bright"
                      >
                        {suggestion}
                      </motion.button>
                    ))}
                  </div>
                </motion.div>
              ) : null}

              {messages.map((message, index) => {
                const isUser = message.role === "user";
                const isLastAssistant =
                  !isUser &&
                  index ===
                    [...messages]
                      .map((item) => item.role)
                      .lastIndexOf("assistant");

                return (
                  <div
                    key={message.id}
                    className={isUser ? "flex justify-end" : "flex justify-start"}
                  >
                    {isUser ? (
                      <motion.div
                        initial={{ opacity: 0, x: 20, scale: 0.95 }}
                        animate={{ opacity: 1, x: 0, scale: 1 }}
                        transition={{ duration: 0.35 }}
                        className="max-w-[70%] rounded-xl rounded-tr-none border border-secondary/20 bg-secondary-container px-6 py-4 text-on-secondary-container shadow-xl backdrop-blur-md"
                      >
                        <p className="text-lg font-medium leading-relaxed">
                          {message.content}
                        </p>
                      </motion.div>
                    ) : (
                      <div className="flex w-full items-start gap-4">
                        <div className="relative shrink-0">
                          <div className="animate-pulse-aura absolute inset-0 translate-y-1 rounded-full bg-primary/40 blur-md" />
                          <div className="relative flex h-10 w-10 items-center justify-center rounded-full border border-primary/30 bg-primary-container shadow-lg">
                            <Bolt className="h-5 w-5 fill-current text-on-primary-container" />
                          </div>
                        </div>

                        <div className="w-full max-w-[85%] space-y-6">
                          <motion.div
                            variants={containerVariants}
                            initial="hidden"
                            animate="visible"
                            className="space-y-6"
                          >
                            <motion.div
                              variants={itemVariants}
                              className="group relative overflow-hidden rounded-xl rounded-tl-none border-l-4 border-primary bg-surface-container-high/40 px-6 py-4 shadow-2xl backdrop-blur-2xl"
                            >
                              <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-transparent opacity-0 transition-opacity duration-700 group-hover:opacity-100" />
                              <div className="relative space-y-3">
                                {formatAssistantText(message.content)}
                              </div>
                            </motion.div>

                            {isLastAssistant ? (
                              <motion.div
                                variants={itemVariants}
                                className="flex flex-wrap gap-3"
                              >
                                {suggestions.map((suggestion) => (
                                  <motion.button
                                    key={suggestion}
                                    whileHover={{ scale: 1.05, y: -2 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={() => setInputValue(suggestion)}
                                    className="rounded-full border border-transparent bg-surface-container-highest/80 px-5 py-2.5 text-sm font-bold text-on-surface shadow-lg backdrop-blur-md transition-all hover:border-white/10 hover:bg-surface-bright"
                                  >
                                    {suggestion}
                                  </motion.button>
                                ))}
                              </motion.div>
                            ) : null}
                          </motion.div>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}

              {pendingUserContent ? (
                <>
                  <div className="flex justify-end">
                    <motion.div
                      initial={{ opacity: 0, x: 20, scale: 0.95 }}
                      animate={{ opacity: 1, x: 0, scale: 1 }}
                      transition={{ duration: 0.25 }}
                      className="max-w-[70%] rounded-xl rounded-tr-none border border-secondary/20 bg-secondary-container px-6 py-4 text-on-secondary-container shadow-xl backdrop-blur-md"
                    >
                      <p className="text-lg font-medium leading-relaxed">
                        {pendingUserContent}
                      </p>
                    </motion.div>
                  </div>

                  <div className="flex items-start gap-4">
                    <div className="relative shrink-0">
                      <div className="animate-pulse-aura absolute inset-0 translate-y-1 rounded-full bg-primary/40 blur-md" />
                      <div className="relative flex h-10 w-10 items-center justify-center rounded-full border border-primary/30 bg-primary-container shadow-lg">
                        <Leaf className="h-5 w-5 text-on-primary-container" />
                      </div>
                    </div>

                    <TypingDots />
                  </div>
                </>
              ) : null}
            </div>
          </div>

          {shouldShowStructuredInsights ? (
            <StructuredInsightsPanel chartData={chartData} insights={insights} />
          ) : null}

          <div className="bg-gradient-to-t from-background via-background/80 to-transparent p-8 backdrop-blur-[2px]">
            {sendMutation.isError ? (
              <div className="mx-auto mb-4 max-w-4xl">
                <ErrorState message={sendMutation.error.message} />
              </div>
            ) : null}

            <div className="group relative mx-auto max-w-4xl">
              <div className="absolute -inset-1 rounded-[1.4rem] bg-gradient-to-r from-primary/30 to-secondary/30 opacity-0 blur-xl transition-opacity duration-1000 group-focus-within:opacity-100" />
              <input
                className="relative w-full rounded-xl border border-white/[0.03] bg-surface-container-low px-8 py-6 pr-20 text-lg font-medium shadow-2xl transition-all placeholder:text-slate-500 focus:border-primary/50 focus:bg-surface-container-high/90 focus:outline-none group-focus-within:backdrop-blur-3xl"
                placeholder="Ask your AI Assistant..."
                type="text"
                value={inputValue}
                onChange={(event) => setInputValue(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && canSend) {
                    event.preventDefault();
                    handleSend(inputValue);
                  }
                }}
              />
              <div className="absolute left-0 top-1/2 h-8 w-1 -translate-y-1/2 rounded-full bg-primary opacity-0 transition-opacity group-focus-within:opacity-100" />
              <button
                type="button"
                disabled={!canSend}
                onClick={() => handleSend(inputValue)}
                className="absolute right-4 top-1/2 flex h-12 w-12 -translate-y-1/2 items-center justify-center rounded-full bg-primary text-on-primary shadow-[0_0_20px_rgba(78,222,163,0.3)] transition-transform duration-150 hover:scale-105 active:scale-95 disabled:opacity-60 group-focus-within:shadow-[0_0_30px_rgba(78,222,163,0.5)]"
              >
                <Send className="h-5 w-5 fill-current" />
              </button>
            </div>
          </div>
        </section>

        <DailyContextPanel
          currentGoal={currentGoal}
          latestSnapshot={latestSnapshot}
        />
      </main>
    </div>
  );
}