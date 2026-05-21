import * as React from "react";
import Link from "next/link";
import { cn } from "@/lib/cn";

type Variant = "primary" | "secondary" | "ghost";

type ButtonProps = {
  variant?: Variant;
  className?: string;
  href?: string;
  children: React.ReactNode;
} & Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, "ref">;

const base =
  "inline-flex items-center justify-center rounded-full px-7 py-3.5 text-button transition-all duration-300 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-surface disabled:opacity-50 disabled:cursor-not-allowed";

const variants: Record<Variant, string> = {
  primary:
    "bg-primary text-white hover:bg-on-surface hover:shadow-vapor active:scale-[0.98]",
  secondary:
    "bg-white/70 text-on-surface backdrop-blur-glass border border-outline-variant hover:bg-white hover:shadow-glass active:scale-[0.98]",
  ghost:
    "text-on-surface hover:text-primary underline-offset-4 hover:underline",
};

export function Button({
  variant = "primary",
  className,
  href,
  children,
  ...props
}: ButtonProps) {
  const classes = cn(base, variants[variant], className);

  if (href) {
    return (
      <Link href={href} className={classes}>
        {children}
      </Link>
    );
  }

  return (
    <button className={classes} {...props}>
      {children}
    </button>
  );
}
