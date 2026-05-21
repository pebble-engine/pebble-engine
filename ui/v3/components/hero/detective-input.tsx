"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Globe, Building2, Sparkles, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { type } from "@/lib/type";
import { EASE_CINEMATIC } from "@/lib/motion";

/* ---------------------------------------------------------------------------
   Detective Input — hero input for the Pebble landing page (light mode).

   Differentiator vs Lovable / v0 / Base44 / Bolt:
   - No mode toggles, no fake "Plan / Generate" buttons.
   - As the user types, a small status line reveals what Pebble detected:
       URL        → brand extraction path
       Industry   → industry-pattern matching path
       Prose      → free-text path
   - Example chips below the field pre-fill and focus — no submit on click.
   - "Switch to Inspired by this design" link only appears on URL detection,
     and fires onSubmit with inspireMode: true.
--------------------------------------------------------------------------- */

/* ---- URL detection (same regex as welcome-phase.tsx looksLikeUrl) ---- */
const URL_LIKE_RX = /^(https?:\/\/)?[a-z0-9-]+(\.[a-z0-9-]+)+(\/\S*)?$/i;

function looksLikeUrl(input: string): boolean {
  const trimmed = input.trim();
  if (!trimmed || trimmed.length > 200) return false;
  if (/\s/.test(trimmed)) return false;
  return URL_LIKE_RX.test(trimmed);
}

/* ---- Industry detection ---- */
const COMMON_INDUSTRIES = [
  "bakery",
  "cafe",
  "coffee shop",
  "restaurant",
  "dental",
  "yoga",
  "law firm",
  "photographer",
  "salon",
  "boutique",
  "gym",
  "fitness",
  "consulting",
  "real estate",
  "agency",
];

function detectIndustry(input: string): string | null {
  const lower = input.toLowerCase();
  for (const industry of COMMON_INDUSTRIES) {
    if (lower.includes(industry)) return industry;
  }
  return null;
}

/* ---- Detection state type ---- */
type DetectionStatus =
  | { kind: "empty" }
  | { kind: "url" }
  | { kind: "industry"; label: string }
  | { kind: "prose" };

function classify(value: string): DetectionStatus {
  const trimmed = value.trim();
  if (!trimmed) return { kind: "empty" };
  if (looksLikeUrl(trimmed)) return { kind: "url" };
  const industry = detectIndustry(trimmed);
  if (industry) return { kind: "industry", label: industry };
  if (trimmed.length >= 10) return { kind: "prose" };
  return { kind: "empty" };
}

/* ---- Default examples ---- */
const EXAMPLES = ["bonappetit.com", "stripe.com", "a bakery in Brooklyn"];

/* ---- Props ---- */
export interface DetectiveInputProps {
  /** Called when the user submits (Enter or Build button). */
  onSubmit: (value: string, opts?: { inspireMode?: boolean }) => void | Promise<void>;
  /** Optional pre-filled value. */
  defaultValue?: string;
  /** Disable the entire panel (e.g. while extraction runs). */
  disabled?: boolean;
  /** Chips shown below the input. */
  examples?: string[];
  autoFocus?: boolean;
}

/* ---- Status line content ---- */
interface StatusContent {
  icon: React.ReactNode;
  text: string;
}

function statusContent(status: DetectionStatus): StatusContent | null {
  switch (status.kind) {
    case "url":
      return {
        icon: <Globe className="w-3.5 h-3.5 shrink-0" />,
        text: "URL detected · we'll extract your brand identity",
      };
    case "industry":
      return {
        icon: <Building2 className="w-3.5 h-3.5 shrink-0" />,
        text: `Looks like a ${status.label} · we'll match industry patterns`,
      };
    case "prose":
      return {
        icon: <Sparkles className="w-3.5 h-3.5 shrink-0" />,
        text: "Got it · we'll work from what you wrote",
      };
    default:
      return null;
  }
}

/* ---- Animated dot ---- */
const StatusDot: React.FC = () => (
  <motion.span
    initial={{ opacity: 0, scale: 0.5 }}
    animate={{ opacity: 1, scale: 1 }}
    exit={{ opacity: 0, scale: 0.5 }}
    transition={{ duration: 0.25, ease: EASE_CINEMATIC }}
    className="inline-block w-2 h-2 rounded-full bg-current shrink-0"
    aria-hidden
  />
);

/* ---- Gradient border keyframes (injected once) ---- */
const GRADIENT_STYLE_ID = "detective-input-gradient-style";
const GRADIENT_CSS = `
@keyframes detective-border-spin {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
.detective-focus-ring {
  position: absolute;
  inset: -1.5px;
  border-radius: inherit;
  pointer-events: none;
  opacity: 0;
  background: linear-gradient(
    270deg,
    #d8d1c5,
    #205661,
    #c76e3a,
    #4b6548,
    #d8d1c5
  );
  background-size: 400% 400%;
  animation: detective-border-spin 6s ease infinite;
  transition: opacity 0.4s ease;
  z-index: 0;
}
.detective-focus-ring.active {
  opacity: 0.55;
}
`;

function useGradientStyle() {
  React.useEffect(() => {
    if (typeof document === "undefined") return;
    if (document.getElementById(GRADIENT_STYLE_ID)) return;
    const tag = document.createElement("style");
    tag.id = GRADIENT_STYLE_ID;
    tag.textContent = GRADIENT_CSS;
    document.head.appendChild(tag);
  }, []);
}

/* ===========================================================================
   Main component
   =========================================================================== */
export function DetectiveInput({
  onSubmit,
  defaultValue = "",
  disabled = false,
  examples = EXAMPLES,
  autoFocus = false,
}: DetectiveInputProps) {
  useGradientStyle();

  const inputRef = React.useRef<HTMLInputElement>(null);
  const [value, setValue] = React.useState(defaultValue);
  const [focused, setFocused] = React.useState(false);
  const [submitting, setSubmitting] = React.useState(false);

  const status = classify(value);
  const content = statusContent(status);
  const isUrl = status.kind === "url";
  const isDisabled = disabled || submitting;

  /* Submit handler */
  const handleSubmit = React.useCallback(
    async (inspireMode = false) => {
      const trimmed = value.trim();
      if (!trimmed || isDisabled) return;
      setSubmitting(true);
      try {
        await onSubmit(trimmed, { inspireMode });
      } finally {
        setSubmitting(false);
      }
    },
    [value, isDisabled, onSubmit],
  );

  /* Keyboard */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void handleSubmit(false);
    }
  };

  /* Chip click: prefill + focus, do NOT submit */
  const handleChipClick = (example: string) => {
    setValue(example);
    requestAnimationFrame(() => inputRef.current?.focus());
  };

  return (
    <div className="flex flex-col gap-3 w-full">
      {/* ---- Card ---- */}
      <div
        className={cn(
          "relative rounded-2xl",
          isDisabled && "opacity-60 pointer-events-none",
        )}
      >
        {/* Animated gradient border (absolute, behind card surface) */}
        <div
          className={cn("detective-focus-ring rounded-2xl", focused && "active")}
          aria-hidden
        />

        {/* Card surface */}
        <div
          className={cn(
            "relative z-10 rounded-2xl bg-card border border-border",
            "shadow-[0_8px_40px_rgba(0,0,0,0.06)]",
            "transition-shadow duration-300",
            focused && "shadow-[0_12px_48px_rgba(0,0,0,0.10)]",
          )}
        >
          {/* Input row */}
          <div className="flex items-center gap-3 px-6 py-5">
            <input
              ref={inputRef}
              type="text"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => setFocused(true)}
              onBlur={() => setFocused(false)}
              placeholder="Enter your website or describe your business…"
              disabled={isDisabled}
              autoFocus={autoFocus}
              className={cn(
                "flex-1 bg-transparent border-none outline-none focus:outline-none",
                "text-lg text-foreground placeholder:text-muted-foreground",
                "leading-snug",
              )}
              aria-label="Describe your business or enter your website"
            />

            {/* Build CTA */}
            <button
              type="button"
              onClick={() => void handleSubmit(false)}
              disabled={isDisabled || !value.trim()}
              className={cn(
                "shrink-0 flex items-center gap-1.5 rounded-full px-6 py-3",
                "bg-foreground text-background text-base font-semibold",
                "transition-all duration-200",
                "hover:opacity-85 active:scale-95",
                "disabled:opacity-40 disabled:cursor-not-allowed",
                "focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
              )}
            >
              {submitting ? (
                <span className={cn(type.body.s, "opacity-70")}>…</span>
              ) : (
                <>
                  Build
                  <ArrowRight className="w-5 h-5" aria-hidden />
                </>
              )}
            </button>
          </div>

          {/* Status line */}
          <AnimatePresence mode="wait">
            {content && (
              <motion.div
                key={status.kind}
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.28, ease: EASE_CINEMATIC }}
                className="overflow-hidden"
              >
                <div className="px-6 pb-4 flex flex-col gap-1.5">
                  {/* Primary status */}
                  <div
                    className={cn(
                      "flex items-center gap-2 text-[14px] text-muted-foreground",
                    )}
                  >
                    <StatusDot />
                    {content.icon}
                    <span>{content.text}</span>
                  </div>

                  {/* URL-only: inspire link */}
                  {isUrl && (
                    <motion.div
                      initial={{ opacity: 0, x: -4 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -4 }}
                      transition={{ duration: 0.22, ease: EASE_CINEMATIC, delay: 0.08 }}
                      className="pl-6"
                    >
                      <button
                        type="button"
                        onClick={() => void handleSubmit(true)}
                        className={cn(
                          "text-[13px] text-muted-foreground underline underline-offset-2",
                          "hover:text-foreground transition-colors duration-150",
                          "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring rounded-sm",
                        )}
                      >
                        ↳ Switch to "Inspired by this design" mode
                      </button>
                    </motion.div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* ---- Example chips ---- */}
      <AnimatePresence>
        {status.kind === "empty" && (
          <motion.div
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 4 }}
            transition={{ duration: 0.25, ease: EASE_CINEMATIC }}
            className="flex flex-wrap items-center gap-x-2 gap-y-1.5 px-1"
          >
            <span className={cn(type.caption, "shrink-0")}>Try:</span>
            {examples.map((example, i) => (
              <React.Fragment key={example}>
                <button
                  type="button"
                  onClick={() => handleChipClick(example)}
                  className={cn(
                    "text-[13px] text-muted-foreground",
                    "hover:text-foreground transition-colors duration-150",
                    "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring rounded-sm",
                  )}
                >
                  {example}
                </button>
                {i < examples.length - 1 && (
                  <span className="text-muted-foreground select-none text-[13px]" aria-hidden>
                    ·
                  </span>
                )}
              </React.Fragment>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default DetectiveInput;
