import * as React from "react";
import Link from "next/link";
import { cn } from "@/lib/cn";

type Variant = "cinematic" | "outline" | "ghost";

type ButtonProps = {
  variant?: Variant;
  className?: string;
  href?: string;
  children: React.ReactNode;
} & Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, "ref">;

const variants: Record<Variant, string> = {
  cinematic: "btn-cinematic",
  outline: "btn-outline",
  ghost:
    "inline-flex items-center justify-center text-button text-fg hover:text-accent underline-offset-4 hover:underline transition-colors",
};

/**
 * Button — three variants tied to the Cinematic IMAX DNA.
 *  - "cinematic" → filled vermilion CTA with gradient overlay sheen
 *  - "outline"   → 1px hollow border that inverts to fill on hover
 *  - "ghost"     → text-only link
 */
export function Button({
  variant = "cinematic",
  className,
  href,
  children,
  ...props
}: ButtonProps) {
  const classes = cn(variants[variant], className);

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
