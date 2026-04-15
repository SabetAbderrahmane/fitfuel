"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight, Info, Loader2 } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { useRegisterMutation } from "@/features/auth/hooks/use-register-mutation";
import {
  signUpSchema,
  type SignUpFormValues,
} from "@/features/auth/schemas/sign-up.schema";

function InputField({
  label,
  type = "text",
  placeholder,
  error,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  error?: string;
}) {
  return (
    <div className="w-full space-y-1">
      <label className="px-1 text-xs font-bold uppercase tracking-widest text-on-surface-variant">
        {label}
      </label>

      <div className="group relative">
        <div className="absolute left-0 top-1/2 h-8 w-1 -translate-y-1/2 rounded-r-full bg-transparent transition-all group-focus-within:bg-primary" />
        <input
          type={type}
          className={`flex w-full rounded-md border-none bg-surface-container-low px-6 py-4 text-on-surface placeholder:text-outline-variant transition-colors focus:bg-surface-container-high focus:ring-0 ${
            error ? "ring-1 ring-error" : ""
          }`}
          placeholder={placeholder}
          {...props}
        />
      </div>

      {error ? <p className="px-1 text-xs text-error">{error}</p> : null}
    </div>
  );
}

function GoogleIcon() {
  return (
    <svg className="h-5 w-5" viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
        fill="#4285F4"
      />
      <path
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
        fill="#34A853"
      />
      <path
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
        fill="#FBBC05"
      />
      <path
        d="M12 5.38c1.62 0 3.06.56 4.21 1.66l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
        fill="#EA4335"
      />
    </svg>
  );
}

export function SignUpForm() {
  const router = useRouter();
  const registerMutation = useRegisterMutation();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignUpFormValues>({
    resolver: zodResolver(signUpSchema),
    defaultValues: {
      fullName: "",
      email: "",
      password: "",
      confirmPassword: "",
    },
    mode: "onBlur",
  });

  const onSubmit = (values: SignUpFormValues) => {
    registerMutation.mutate(
      {
        email: values.email.trim(),
        username: values.fullName.trim(),
        password: values.password,
      },
      {
        onSuccess: () => {
          router.replace("/login");
        },
      }
    );
  };

  return (
    <>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
        <InputField
          label="Full Name"
          placeholder="John Doe"
          {...register("fullName")}
          error={errors.fullName?.message}
        />

        <InputField
          label="Email"
          type="email"
          placeholder="john@example.com"
          autoComplete="email"
          {...register("email")}
          error={errors.email?.message}
        />

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <InputField
            label="Password"
            type="password"
            placeholder="••••••••"
            autoComplete="new-password"
            {...register("password")}
            error={errors.password?.message}
          />

          <InputField
            label="Confirm"
            type="password"
            placeholder="••••••••"
            autoComplete="new-password"
            {...register("confirmPassword")}
            error={errors.confirmPassword?.message}
          />
        </div>

        <div className="rounded-xl bg-surface-container-low/80 px-4 py-3">
          <p className="flex items-center gap-2 px-1 text-[11px] italic text-on-surface-variant/80">
            <Info className="h-4 w-4 text-secondary" />
            We&apos;ll use this to calculate your goals and metabolic profile.
          </p>
        </div>

        {registerMutation.isError ? (
          <div
            className="rounded-xl bg-error/10 px-4 py-3 text-sm text-error"
            aria-live="polite"
          >
            {registerMutation.error.message}
          </div>
        ) : null}

        <button
          type="submit"
          disabled={registerMutation.isPending}
          className="shimmer-effect inline-flex w-full items-center justify-center gap-2 rounded-full bg-primary px-6 py-4 text-base font-bold text-on-primary shadow-[0_0_15px_rgba(78,222,163,0.2)] transition-all hover:shadow-[0_0_25px_rgba(78,222,163,0.4)] disabled:pointer-events-none disabled:opacity-50"
        >
          {registerMutation.isPending ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" />
              Creating Account...
            </>
          ) : (
            <>
              Create Account
              <ArrowRight className="h-5 w-5" />
            </>
          )}
        </button>
      </form>

      <div className="my-8 flex items-center">
        <div className="flex-grow border-t border-outline-variant/20" />
        <span className="px-4 text-xs font-bold uppercase text-outline-variant">
          OR
        </span>
        <div className="flex-grow border-t border-outline-variant/20" />
      </div>

      <button
        type="button"
        disabled
        className="inline-flex w-full items-center justify-center gap-3 rounded-full bg-surface-container-highest px-6 py-4 text-base font-bold text-on-surface transition-all hover:bg-surface-bright disabled:opacity-100"
      >
        <GoogleIcon />
        Continue with Google
      </button>

      <footer className="mt-10 text-center">
        <p className="text-sm text-on-surface-variant">
          Already have an account?{" "}
          <Link href="/login" className="font-bold text-primary hover:underline">
            Log in
          </Link>
        </p>
      </footer>
    </>
  );
}