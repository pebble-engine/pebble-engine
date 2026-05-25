import { cn } from "@/lib/cn";
import type { ComponentPropsWithoutRef, ElementType } from "react";

type Variant = "primary" | "secondary";
type Size = "default" | "lg";

type ButtonProps<T extends ElementType = "button"> = {
  variant?: Variant;
  size?: Size;
  as?: T;
} & Omit<ComponentPropsWithoutRef<T>, "as">;

export function Button<T extends ElementType = "button">({
  variant = "primary",
  size = "default",
  as,
  className,
  children,
  ...rest
}: ButtonProps<T>) {
  const Tag = (as ?? "button") as ElementType;

  return (
    <Tag
      className={cn(
        "inline-flex items-center justify-center rounded-full font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)] focus-visible:ring-offset-2",
        variant === "primary" &&
          "bg-[var(--color-accent)] hover:bg-[var(--color-accent-dark)] text-white",
        variant === "secondary" &&
          "bg-white border border-[var(--color-border)] text-[var(--color-text-primary)] hover:bg-[var(--color-surface-2)]",
        size === "default" && "h-12 px-6 text-[15px]",
        size === "lg" && "h-14 px-8 text-[16px]",
        className
      )}
      {...rest}
    >
      {children}
    </Tag>
  );
}
