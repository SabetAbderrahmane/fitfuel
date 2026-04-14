"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { zodResolver } from "@hookform/resolvers/zod";
import { Controller, useForm } from "react-hook-form";
import { ArrowRight, Eye, EyeOff, Zap } from "lucide-react";

import { LoadingState } from "@/components/states/loading-state";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useLoginMutation } from "@/features/auth/hooks/use-login-mutation";
import {
  loginSchema,
  type LoginFormValues,
} from "@/features/auth/schemas/login.schema";
import { cn } from "@/lib/utils/cn";

function GoogleMark() {
  return (
    <span className="inline-flex h-5 w-5 items-center justify-center rounded-sm bg-white/10 text-[11px] font-bold text-slate-200">
      G
    </span>
  );
}

export function LoginForm() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const loginMutation = useLoginMutation();

  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
      rememberMe: true,
    },
    mode: "onBlur",
  });

  const onSubmit = (values: LoginFormValues) => {
    loginMutation.mutate(values, {
      onSuccess: () => {
        router.replace("/dashboard");
      },
    });
  };

  const submitError =
    loginMutation.isError && loginMutation.error.message
      ? loginMutation.error.message
      : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 22, scale: 0.985 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.45, ease: "easeOut" }}
    >
      <Card className="overflow-hidden rounded-4xl border border-white/10 bg-white/8 shadow-[0_30px_90px_rgba(2,8,23,0.75)] backdrop-blur-2xl">
        <CardContent className="px-6 py-8 sm:px-10 sm:py-10">
          <div className="mb-8 flex justify-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[#10b981] shadow-[0_0_40px_rgba(16,185,129,0.28)]">
              <Zap className="h-8 w-8 fill-[#05211d] text-[#05211d]" />
            </div>
          </div>

          <div className="mb-8 text-center">
            <h1 className="text-balance text-4xl font-semibold tracking-tight text-white sm:text-[3rem]">
              Welcome back
            </h1>
            <p className="mt-2 text-base text-slate-300 sm:text-lg">
              Continue your journey with FitFuel AI
            </p>
          </div>

          <form onSubmit={form.handleSubmit(onSubmit)} noValidate className="space-y-6">
            <fieldset disabled={loginMutation.isPending} className="space-y-6">
              <div className="space-y-2.5">
                <Label
                  htmlFor="email"
                  className="text-[0.9rem] font-semibold uppercase tracking-[0.22em] text-slate-200"
                >
                  Email Address
                </Label>
                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  placeholder="name@domain.com"
                  className={cn(
                    "h-15 rounded-2xl border-white/5 bg-[#0a1630]/90 px-5 text-base text-white placeholder:text-slate-500 focus-visible:border-emerald-400/50 focus-visible:ring-emerald-400/30 sm:h-16 sm:text-lg",
                    form.formState.errors.email && "border-red-400/40"
                  )}
                  {...form.register("email")}
                />
                {form.formState.errors.email ? (
                  <p className="text-sm text-red-300" role="alert">
                    {form.formState.errors.email.message}
                  </p>
                ) : null}
              </div>

              <div className="space-y-2.5">
                <div className="flex items-center justify-between gap-3">
                  <Label
                    htmlFor="password"
                    className="text-[0.9rem] font-semibold uppercase tracking-[0.22em] text-slate-200"
                  >
                    Password
                  </Label>

                  <Link
                    href="/login#forgot-password"
                    className="text-sm font-semibold text-emerald-400 transition hover:text-emerald-300"
                  >
                    Forgot Password?
                  </Link>
                </div>

                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="current-password"
                    placeholder="••••••••"
                    className={cn(
                      "h-15 rounded-2xl border-white/5 bg-[#0a1630]/90 px-5 pr-14 text-base text-white placeholder:text-slate-500 focus-visible:border-emerald-400/50 focus-visible:ring-emerald-400/30 sm:h-16 sm:text-lg",
                      form.formState.errors.password && "border-red-400/40"
                    )}
                    {...form.register("password")}
                  />
                  <button
                    type="button"
                    aria-label={showPassword ? "Hide password" : "Show password"}
                    onClick={() => setShowPassword((current) => !current)}
                    className="absolute right-4 top-1/2 inline-flex -translate-y-1/2 items-center justify-center text-slate-400 transition hover:text-slate-200"
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5" />
                    ) : (
                      <Eye className="h-5 w-5" />
                    )}
                  </button>
                </div>

                {form.formState.errors.password ? (
                  <p className="text-sm text-red-300" role="alert">
                    {form.formState.errors.password.message}
                  </p>
                ) : null}
              </div>

              <div className="flex items-center justify-between gap-4">
                <Controller
                  control={form.control}
                  name="rememberMe"
                  render={({ field }) => (
                    <div className="flex items-center gap-2.5">
                      <Checkbox
                        id="rememberMe"
                        checked={field.value}
                        onCheckedChange={(checked: boolean | "indeterminate") =>field.onChange(checked === true)}
                        className="border-white/20 data-[state=checked]:border-emerald-500 data-[state=checked]:bg-emerald-500"
                      />
                      <Label
                        htmlFor="rememberMe"
                        className="cursor-pointer text-sm text-slate-300"
                      >
                        Remember me
                      </Label>
                    </div>
                  )}
                />
              </div>

              {submitError ? (
                <div
                  className="rounded-2xl border border-red-400/20 bg-red-500/10 px-4 py-3 text-sm text-red-200"
                  aria-live="polite"
                >
                  {submitError}
                </div>
              ) : null}

              <Button
                type="submit"
                disabled={loginMutation.isPending}
                className="h-16 w-full rounded-full bg-[#55d5a2] text-xl font-semibold text-[#05221c] shadow-[0_0_30px_rgba(16,185,129,0.22)] transition hover:bg-[#6be0b2] disabled:opacity-90"
              >
                {loginMutation.isPending ? (
                  <LoadingState label="Logging in..." className="text-[#05221c]" />
                ) : (
                  <span className="inline-flex items-center gap-3">
                    <span>Log In</span>
                    <ArrowRight className="h-5 w-5" />
                  </span>
                )}
              </Button>
            </fieldset>
          </form>

          <div className="my-8 flex items-center gap-4">
            <div className="h-px flex-1 bg-white/8" />
            <span className="text-xs font-semibold uppercase tracking-[0.26em] text-slate-500">
              Or continue with
            </span>
            <div className="h-px flex-1 bg-white/8" />
          </div>

          <Button
            type="button"
            disabled
            className="h-15 w-full rounded-full border border-white/8 bg-white/8 text-lg font-medium text-slate-200 backdrop-blur-xl transition hover:bg-white/10 sm:h-16"
          >
            <span className="inline-flex items-center gap-3">
              <GoogleMark />
              <span>Sign in with Google</span>
            </span>
          </Button>

          <p className="mt-10 text-center text-base text-slate-300 sm:text-lg">
            Don&apos;t have an account?{" "}
            <Link
              href="/sign-up"
              className="font-semibold text-[#f59e0b] transition hover:text-[#fbbf24]"
            >
              Sign up
            </Link>
          </p>
        </CardContent>
      </Card>
    </motion.div>
  );
}