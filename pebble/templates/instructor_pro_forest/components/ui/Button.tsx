import Link from "next/link";
import { cn } from "@/lib/cn";
import type { ComponentProps, ReactNode } from "react";

type Variant = "primary" | "secondary" | "ghost" | "gold";
type Size = "sm" | "md" | "lg";

const VARIANT_STYLES: Record<Variant, string> = {
  primary:
    "bg-accent text-fg hover:bg-[hsl(var(--accent-light))] focus-visible:ring-accent border border-accent/40",
  secondary:
    "bg-card text-fg hover:border-accent/60 border border-border focus-visible:ring-accent",
  ghost:
    "bg-transparent text-fg hover:bg-card border border-transparent focus-visible:ring-accent",
  gold:
    "bg-[hsl(var(--accent-warm))] text-[hsl(var(--bg))] hover:bg-[hsl(var(--accent-warm-light))] focus-visible:ring-[hsl(var(--accent-warm))] border border-[hsl(var(--accent-warm))]/50 font-semibold",
};

const SIZE_STYLES: Record<Size, string> = {
  sm: "px-4 py-2 text-xs tracking-wide-12",
  md: "px-5 py-2.5 text-sm tracking-wide-12",
  lg: "px-7 py-3.5 text-sm tracking-wide-12",
};

const BASE =
  "inline-flex items-center justify-center gap-2 rounded-full font-bold uppercase transition-all duration-200 hover:scale-[1.02] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-bg disabled:opacity-50 disabled:pointer-events-none";

type CommonProps = {
  variant?: Variant;
  size?: Size;
  className?: string;
  children: ReactNode;
  shimmer?: boolean;
};

type LinkProps = CommonProps & { href: string } & Omit<ComponentProps<typeof Link>, "href" | "className" | "children">;
type ButtonProps = CommonProps & { href?: undefined } & Omit<ComponentProps<"button">, "className" | "children">;

export function Button(props: LinkProps | ButtonProps) {
  const { variant = "primary", size = "md", className, children, shimmer, ...rest } = props;
  const classes = cn(
    BASE,
    VARIANT_STYLES[variant],
    SIZE_STYLES[size],
    shimmer && "shimmer-band",
    className,
  );

  if ("href" in props && props.href) {
    const { href, ...linkRest } = rest as LinkProps;
    return (
      <Link href={href} className={classes} {...linkRest}>
        {children}
      </Link>
    );
  }

  return (
    <button className={classes} {...(rest as ComponentProps<"button">)}>
      {children}
    </button>
  );
}
