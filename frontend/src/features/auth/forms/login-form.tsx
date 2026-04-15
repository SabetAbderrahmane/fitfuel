"use client";

import Link from "next/link";
import { useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { ArrowRight, Eye, EyeOff, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";

import { useLoginMutation } from "@/features/auth/hooks/use-login-mutation";
import {
  loginSchema,
  type LoginFormValues,
} from "@/features/auth/schemas/login.schema";

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

  return (
    <form className="space-y-6" onSubmit={form.handleSubmit(onSubmit)} noValidate>
      <div className="space-y-2">
        <label
          className="block text-xs font-bold uppercase tracking-widest text-on-surface-variant px-1"
          htmlFor="email"
        >
          Email Address
        </label>

        <div className="relative">
          <input
            id="email"
            type="email"
            placeholder="name@company.com"
            autoComplete="email"
            className="peer w-full bg-surface-container-low border-none rounded-md px-4 py-4 text-on-surface focus:ring-2 focus:ring-primary/20 focus:bg-surface-container-high transition-all outline-none"
            {...form.register("email")}
          />
          <div className="pointer-events-none absolute left-0 top-1/4 h-1/2 w-1 bg-primary rounded-full opacity-0 peer-focus:opacity-100 transition-opacity" />
        </div>

        {form.formState.errors.email ? (
          <p className="px-1 text-sm text-[#ffb4ab]" role="alert">
            {form.formState.errors.email.message}
          </p>
        ) : null}
      </div>

      <div className="space-y-2">
        <div className="flex justify-between items-end px-1">
          <label
            className="text-xs font-bold uppercase tracking-widest text-on-surface-variant"
            htmlFor="password"
          >
            Password
          </label>

          <Link
            className="text-xs font-bold text-primary hover:text-primary/80 transition-colors"
            href="/login#forgot-password"
          >
            Forgot password?
          </Link>
        </div>

        <div className="relative group/pass">
          <input
            id="password"
            type={showPassword ? "text" : "password"}
            placeholder="••••••••"
            autoComplete="current-password"
            className="peer w-full bg-surface-container-low border-none rounded-md px-4 py-4 text-on-surface focus:ring-2 focus:ring-primary/20 focus:bg-surface-container-high transition-all outline-none"
            {...form.register("password")}
          />

          <button
            onClick={() => setShowPassword((current) => !current)}
            className="absolute right-4 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-white transition-colors"
            type="button"
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
          </button>
        </div>

        {form.formState.errors.password ? (
          <p className="px-1 text-sm text-[#ffb4ab]" role="alert">
            {form.formState.errors.password.message}
          </p>
        ) : null}
      </div>

      <Controller
        control={form.control}
        name="rememberMe"
        render={({ field }) => (
          <div className="flex items-center">
            <input
              id="remember"
              type="checkbox"
              checked={field.value}
              onChange={(event) => field.onChange(event.target.checked)}
              className="w-5 h-5 rounded border-none bg-surface-container-low text-primary accent-[#4edea3] focus:ring-primary/20"
            />
            <label
              className="ml-3 text-sm text-on-surface-variant"
              htmlFor="remember"
            >
              Keep me logged in
            </label>
          </div>
        )}
      />

      {loginMutation.isError ? (
        <div
          className="rounded-xl bg-[#ffb4ab]/10 px-4 py-3 text-sm text-[#ffb4ab]"
          aria-live="polite"
        >
          {loginMutation.error.message}
        </div>
      ) : null}

      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="w-full bg-primary text-on-primary font-bold py-4 rounded-full shadow-[0_8px_30px_rgb(78,222,163,0.2)] hover:shadow-[0_8px_40px_rgb(78,222,163,0.4)] transition-all flex items-center justify-center gap-2 group disabled:opacity-70"
        type="submit"
        disabled={loginMutation.isPending}
      >
        {loginMutation.isPending ? (
          <>
            <Loader2 className="animate-spin" size={20} />
            Logging in...
          </>
        ) : (
          <>
            Log In
            <ArrowRight
              className="group-hover:translate-x-1 transition-transform"
              size={20}
            />
          </>
        )}
      </motion.button>
    </form>
  );
}