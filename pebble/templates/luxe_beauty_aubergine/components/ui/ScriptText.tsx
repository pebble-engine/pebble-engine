import * as React from "react";
import { cn } from "@/lib/cn";

type ScriptTextProps = {
  children: React.ReactNode;
  className?: string;
  as?: "span" | "p" | "div";
};

/**
 * ScriptText — wraps cursive accent copy in Pinyon Script (DNA accent font).
 * Use SPARINGLY: category whisper-text, eyebrow accents, marketing labels.
 * NEVER for body copy or primary h1.
 */
export function ScriptText({ children, className, as = "span" }: ScriptTextProps) {
  const Tag = as;
  return (
    <Tag
      className={cn(
        "font-script text-tertiary leading-none",
        className,
      )}
    >
      {children}
    </Tag>
  );
}
