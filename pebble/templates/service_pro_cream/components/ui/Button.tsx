import Link from "next/link";
import { cn } from "@/lib/cn";
import type { ComponentProps, ReactNode } from "react";

type Variant = "primary" | "secondary" | "ghost";
type Size = "md" | "lg";

const VARIANT_STYLES: Record<Variant, string> = {
  primary:
    "bg-primary text-white hover:bg-secondary focus-visible:ring-primary border border-primary/40",
  secondary:
    "bg-card text-fg hover:border-primary/60 border border-border focus-visible:ring-primary",
  ghost:
    "bg-transparent text-fg hover:bg-card border border-transparent focus-visible:ring-primary",
};

const SIZE_STYLES: Record<Size, string> = {
  md: "px-5 py-2.5 text-sm",
  lg: "px-7 py-3.5 text-base",
};

const BASE =
  "inline-flex items-center justify-center gap-2 rounded-full font-medium tracking-tight transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-bg disabled:opacity-50 disabled:pointer-events-none";

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
    shimmer && "shimmer-sweep",
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
