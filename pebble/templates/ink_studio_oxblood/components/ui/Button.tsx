import * as React from "react";
import Link from "next/link";
import { cn } from "@/lib/cn";

type Variant = "primary" | "secondary" | "ghost";
type Size = "md" | "lg";

type ButtonProps = {
  variant?: Variant;
  size?: Size;
  className?: string;
  href?: string;
  children: React.ReactNode;
} & Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, "ref">;

const base =
  "inline-flex items-center justify-center text-button transition-all duration-300 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink-primary focus-visible:ring-offset-2 focus-visible:ring-offset-ink-bg disabled:opacity-50 disabled:cursor-not-allowed";

const sizes: Record<Size, string> = {
  md: "px-6 py-3",
  lg: "px-8 py-4 text-base tracking-[0.22em]",
};

const variants: Record<Variant, string> = {
  // Filled gold — the primary "Book" CTA. Hover lifts text shadow.
  primary:
    "bg-ink-primary text-ink-bg hover:bg-ink-gold-light hover:shadow-gold active:scale-[0.98]",
  // Outline gold — secondary CTA, sits next to primary.
  secondary:
    "border border-ink-primary text-ink-primary bg-transparent hover:bg-ink-primary/10 hover:shadow-gold active:scale-[0.98]",
  // Bare link style with gold underline.
  ghost:
    "text-ink-fg hover:text-ink-primary underline-offset-4 hover:underline",
};

export function Button({
  variant = "primary",
  size = "md",
  className,
  href,
  children,
  ...props
}: ButtonProps) {
  const classes = cn(base, sizes[size], variants[variant], className);

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
