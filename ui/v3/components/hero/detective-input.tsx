"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Globe,
  Building2,
  Sparkles,
  ArrowRight,
  Paperclip,
  Mic,
  Square,
  X,
  ClipboardList,
  Lock,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { type } from "@/lib/type";
import { EASE_CINEMATIC } from "@/lib/motion";

/* ---------------------------------------------------------------------------
   Detective Input — hero input for the Pebble landing page (light mode).

   Phase 40h (2026-05-21) — Marc's six-pack request:
   1) "Add Files" button for image uploads (passed to onSubmit via opts.files)
   2) "Plan first" toggle (opts.planMode) — sends to /api/plan instead of
      committing the build credit; cheap preview of the 7-field Pebble Plan
   3) Voice / speech-to-text (Web Speech API; mic button hidden if browser
      doesn't support it — so no broken UI on Firefox)
   4) Glowing send button once value is unlocked (non-empty)
   5) Rotating clickable suggestions beneath the bar — one at a time,
      "Can't think of anything? Give these a try:" + a single fading chip
      that cycles every 4s. Click fills the input.
   6) Typewriter placeholder cycle — 10 example briefs type out and erase
      themselves like someone with too many ideas. Stops the moment the
      user types something; resumes if they clear the field.

   Differentiator vs Lovable / v0 / Base44 / Bolt is preserved:
   - The status line still tells the user what we detected as they type.
   - Plan mode + voice + uploads exist but stay quiet until invoked.
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

/* ---- Typewriter placeholders — 10 examples that cycle through the
       placeholder slot when the input is empty.
       Phase 40l (2026-05-21) — every placeholder opens with "Hey
       Pebble! Build" so the field reads conversationally.
       Phase 40m (2026-05-21) — bodies tightened so the full prompt
       (prefix + body) fits comfortably on one line at text-base/lg,
       even on the narrower mobile breakpoints. */
const PLACEHOLDER_PREFIX = "Hey Pebble! Build ";
const PLACEHOLDER_BODIES: string[] = [
  "a bakery in Brooklyn",
  "a yoga studio site",
  "a brewery taproom site",
  "a wedding portfolio",
  "a real-estate brokerage",
  "an auto repair shop",
  "a personal-training site",
  "a Mediterranean restaurant",
  "a salon with online booking",
  "a freelance designer portfolio",
];
/* Phase 40o (2026-05-21) — PLACEHOLDER_EXAMPLES (the merged list)
   removed. The typewriter hook now reads PLACEHOLDER_BODIES directly
   and re-applies the PLACEHOLDER_PREFIX on every render frame, so the
   prefix is ALWAYS visible and only the body types/erases. Marc
   reported the prefix was "snapping back" every cycle — that was the
   prefix being deleted + re-typed each iteration. */

/* ---- Rotating suggestions below the bar. One at a time, fading
       in/out. Clicking fills the input (same as the old chips). These
       are intentionally different from the placeholder cycle so the
       user sees variety. ---- */
const ROTATING_SUGGESTIONS: string[] = [
  "a flower shop with same-day delivery",
  "a tattoo studio with artist portfolios",
  "a moving company with instant quote form",
  "a pet groomer with online booking",
  "a tax-prep CPA with secure document upload",
  "a private chef with weekly menu signup",
  "a music teacher with lesson scheduler",
  "a landscape designer portfolio + consult form",
  "a cleaning service with recurring booking",
  "a food truck with location tracker",
];

/* ---- File upload limits ---- */
const MAX_FILES        = 5;
const MAX_FILE_BYTES   = 10 * 1024 * 1024; // 10MB each
const ACCEPT_MIME      = "image/png,image/jpeg,image/webp,image/gif,image/svg+xml";

/* ---- Web Speech API minimal type shims (the standard lib doesn't
       declare SpeechRecognition since it's still a draft API). ---- */
interface MinimalSpeechRecognitionResult {
  0: { transcript: string };
  isFinal: boolean;
}
interface MinimalSpeechRecognitionEvent extends Event {
  resultIndex: number;
  results: ArrayLike<MinimalSpeechRecognitionResult>;
}
interface MinimalSpeechRecognition extends EventTarget {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  start(): void;
  stop(): void;
  abort(): void;
  onresult: ((this: MinimalSpeechRecognition, ev: MinimalSpeechRecognitionEvent) => void) | null;
  onend:    ((this: MinimalSpeechRecognition, ev: Event) => void) | null;
  onerror:  ((this: MinimalSpeechRecognition, ev: Event) => void) | null;
}
type SpeechRecognitionCtor = new () => MinimalSpeechRecognition;
function getSpeechRecognitionCtor(): SpeechRecognitionCtor | null {
  if (typeof window === "undefined") return null;
  const w = window as unknown as {
    SpeechRecognition?:       SpeechRecognitionCtor;
    webkitSpeechRecognition?: SpeechRecognitionCtor;
  };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
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

/* ---- Gradient border + send-button glow keyframes (injected once) ---- */
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

/* Phase 40h — Send-button glow.
   Fires once value.trim() is non-empty. Pulsing box-shadow in the Pebble
   blue (#3054ff) so the button feels alive + "ready to send". Disabled
   state strips this; we only add the class when unlocked. */
@keyframes detective-send-pulse {
  0%, 100% {
    box-shadow:
      0 0 0 0 rgba(48, 84, 255, 0.55),
      0 6px 24px rgba(48, 84, 255, 0.28);
  }
  50% {
    box-shadow:
      0 0 0 8px rgba(48, 84, 255, 0),
      0 10px 32px rgba(48, 84, 255, 0.36);
  }
}
.detective-send-glow {
  animation: detective-send-pulse 1.8s ease-in-out infinite;
}

/* Mic recording pulse — red, slower */
@keyframes detective-mic-pulse {
  0%, 100% { box-shadow: 0 0 0 0   rgba(220, 38, 38, 0.55); }
  50%      { box-shadow: 0 0 0 6px rgba(220, 38, 38, 0);    }
}
.detective-mic-recording {
  animation: detective-mic-pulse 1.4s ease-in-out infinite;
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

/* ---- Typewriter placeholder hook ----
   Cycles through the example briefs character-by-character while the
   input is empty. Stops the moment the user types something. Resumes
   if they clear the field. */
function useTypewriterPlaceholder(active: boolean): string {
  // Phase 40o (2026-05-21) — Prefix is always present. State holds the
  // BODY suffix only; we render PLACEHOLDER_PREFIX + body downstream.
  // This kills the "snap back to placeholder" Marc reported — the user
  // sees "Hey Pebble! Build" as a stable anchor and only the body
  // portion types/erases between cycles.
  const [body, setBody] = React.useState("");
  const idxRef     = React.useRef(0);
  const phaseRef   = React.useRef<"typing" | "holding" | "deleting" | "pausing">("typing");
  const charRef    = React.useRef(0);

  React.useEffect(() => {
    if (!active) return;
    let cancelled = false;
    let timeoutId: ReturnType<typeof setTimeout> | null = null;

    // Phase 40o pacing — slowed a tiny bit from 40n per Marc's feedback.
    // Still snappier than the original 40h pacing (55/28/1600/250), just
    // not break-neck. ~2.6s per full cycle for a ~30-char body.
    const TYPE_MS   = 28;   // per char while typing
    const DELETE_MS = 14;   // per char while erasing
    const HOLD_MS   = 1100; // pause when fully typed
    const PAUSE_MS  = 180;  // pause when fully erased

    const tick = () => {
      if (cancelled) return;
      const bodyText = PLACEHOLDER_BODIES[idxRef.current];

      if (phaseRef.current === "typing") {
        if (charRef.current < bodyText.length) {
          charRef.current += 1;
          setBody(bodyText.slice(0, charRef.current));
          timeoutId = setTimeout(tick, TYPE_MS);
        } else {
          phaseRef.current = "holding";
          timeoutId = setTimeout(tick, HOLD_MS);
        }
      } else if (phaseRef.current === "holding") {
        phaseRef.current = "deleting";
        timeoutId = setTimeout(tick, DELETE_MS);
      } else if (phaseRef.current === "deleting") {
        if (charRef.current > 0) {
          charRef.current -= 1;
          setBody(bodyText.slice(0, charRef.current));
          timeoutId = setTimeout(tick, DELETE_MS);
        } else {
          phaseRef.current = "pausing";
          timeoutId = setTimeout(tick, PAUSE_MS);
        }
      } else if (phaseRef.current === "pausing") {
        idxRef.current = (idxRef.current + 1) % PLACEHOLDER_BODIES.length;
        phaseRef.current = "typing";
        timeoutId = setTimeout(tick, TYPE_MS);
      }
    };

    timeoutId = setTimeout(tick, TYPE_MS);
    return () => {
      cancelled = true;
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [active]);

  // Prefix + body. When the hook isn't active we still want the prefix
  // to show as a static placeholder so the field never looks empty.
  return PLACEHOLDER_PREFIX + body;
}

/* ---- Rotating suggestion hook ----
   Returns the index of the currently-displayed suggestion + an "epoch"
   counter that AnimatePresence keys off of to fade between them. */
function useRotatingSuggestion(active: boolean, intervalMs = 4000) {
  const [idx, setIdx] = React.useState(() =>
    Math.floor(Math.random() * ROTATING_SUGGESTIONS.length),
  );
  React.useEffect(() => {
    if (!active) return;
    const id = window.setInterval(() => {
      setIdx((cur) => (cur + 1) % ROTATING_SUGGESTIONS.length);
    }, intervalMs);
    return () => window.clearInterval(id);
  }, [active, intervalMs]);
  return { idx, suggestion: ROTATING_SUGGESTIONS[idx] };
}

/* ---- Props ---- */
export interface DetectiveInputProps {
  /** Called when the user submits (Enter or Build button).
      `opts.files` is non-empty when the user attached images.
      `opts.planMode` is true when the user toggled "Plan first" — caller
      should hit /api/plan instead of committing the build credit.
      `opts.inspireMode` is true when the user clicked the inspire link. */
  onSubmit: (
    value: string,
    opts?: { inspireMode?: boolean; planMode?: boolean; files?: File[] },
  ) => void | Promise<void>;
  /** Optional pre-filled value. */
  defaultValue?: string;
  /** Disable the entire panel (e.g. while extraction runs). */
  disabled?: boolean;
  autoFocus?: boolean;
  /** Phase 43.16 — when true, the attach-files button shows a lock
      badge and pops a tooltip on hover/click instead of opening the
      file picker. Used for logged-out visitors. */
  attachLocked?: boolean;
}

/* ===========================================================================
   Main component
   =========================================================================== */
export function DetectiveInput({
  onSubmit,
  defaultValue = "",
  disabled = false,
  autoFocus = false,
  attachLocked = false,
}: DetectiveInputProps) {
  useGradientStyle();

  const inputRef    = React.useRef<HTMLInputElement>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);
  const recognitionRef = React.useRef<MinimalSpeechRecognition | null>(null);
  const valueBeforeSpeechRef = React.useRef<string>("");

  const [value, setValue]            = React.useState(defaultValue);
  const [focused, setFocused]        = React.useState(false);
  const [submitting, setSubmitting]  = React.useState(false);
  const [files, setFiles]            = React.useState<File[]>([]);
  const [planMode, setPlanMode]      = React.useState(false);
  const [listening, setListening]    = React.useState(false);
  const [fileError, setFileError]    = React.useState<string | null>(null);
  const [speechSupported, setSpeechSupported] = React.useState(false);
  // Phase 43.16 — lock tooltip for the attach-files button when
  // attachLocked is true. Shows on hover; click also triggers it +
  // auto-hides after 2.5s (so touch users get the same affordance).
  const [showLockTip, setShowLockTip] = React.useState(false);
  const lockTipTimer = React.useRef<ReturnType<typeof setTimeout> | null>(null);

  React.useEffect(() => {
    setSpeechSupported(getSpeechRecognitionCtor() !== null);
  }, []);

  const status      = classify(value);
  const content     = statusContent(status);
  const isUrl       = status.kind === "url";
  const isDisabled  = disabled || submitting;
  const hasValue    = value.trim().length > 0;
  // Typewriter only runs when the input is genuinely empty AND the user
  // isn't actively recording (we'd be writing into `value` from speech).
  const typewriter  = useTypewriterPlaceholder(!hasValue && !listening && !isDisabled);
  // Rotating suggestion runs whenever the input is empty.
  const rotating    = useRotatingSuggestion(!hasValue);

  /* ---- File picker handlers ---- */
  const handleFilePick = () => {
    if (attachLocked) {
      // Phase 43.16 — pop the tooltip + auto-hide after 2.5s. Don't
      // open the file picker. Same affordance for touch + desktop.
      setShowLockTip(true);
      if (lockTipTimer.current) clearTimeout(lockTipTimer.current);
      lockTipTimer.current = setTimeout(() => setShowLockTip(false), 2500);
      return;
    }
    setFileError(null);
    fileInputRef.current?.click();
  };
  const handleFilesChosen = (chosen: FileList | null) => {
    if (!chosen) return;
    const incoming = Array.from(chosen);
    const next: File[] = [...files];
    for (const f of incoming) {
      if (next.length >= MAX_FILES) {
        setFileError(`Max ${MAX_FILES} images. Remove one to add more.`);
        break;
      }
      if (!f.type.startsWith("image/")) {
        setFileError("Only image files are accepted.");
        continue;
      }
      if (f.size > MAX_FILE_BYTES) {
        setFileError(`${f.name} is over 10MB — too big.`);
        continue;
      }
      next.push(f);
    }
    setFiles(next);
    // Reset so picking the same file twice re-fires onChange.
    if (fileInputRef.current) fileInputRef.current.value = "";
  };
  const removeFile = (i: number) =>
    setFiles((cur) => cur.filter((_, idx) => idx !== i));

  /* ---- Speech recognition handlers ---- */
  const startListening = () => {
    const Ctor = getSpeechRecognitionCtor();
    if (!Ctor) return;
    if (recognitionRef.current) {
      try { recognitionRef.current.abort(); } catch { /* noop */ }
    }
    const rec = new Ctor();
    rec.lang = "en-US";
    rec.continuous = true;
    rec.interimResults = true;
    valueBeforeSpeechRef.current = value;
    rec.onresult = (e) => {
      let transcript = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        transcript += e.results[i][0].transcript;
      }
      const prefix = valueBeforeSpeechRef.current;
      const joiner = prefix && !prefix.endsWith(" ") ? " " : "";
      setValue((prefix + joiner + transcript).trimStart());
    };
    rec.onend   = () => setListening(false);
    rec.onerror = () => setListening(false);
    recognitionRef.current = rec;
    try {
      rec.start();
      setListening(true);
    } catch {
      // Some browsers throw if start() is called twice in a row.
      setListening(false);
    }
  };
  const stopListening = () => {
    try { recognitionRef.current?.stop(); } catch { /* noop */ }
    setListening(false);
  };
  // Make sure recognition is torn down if the component unmounts mid-record.
  React.useEffect(() => () => {
    try { recognitionRef.current?.abort(); } catch { /* noop */ }
  }, []);

  /* ---- Submit ---- */
  const handleSubmit = React.useCallback(
    async (inspireMode = false) => {
      const trimmed = value.trim();
      if (!trimmed || isDisabled) return;
      // If the user is still recording, stop first so the final transcript
      // is committed before we fire.
      if (listening) stopListening();
      setSubmitting(true);
      try {
        await onSubmit(trimmed, {
          inspireMode,
          planMode,
          files: files.length > 0 ? files : undefined,
        });
      } finally {
        setSubmitting(false);
      }
    },
    [value, isDisabled, listening, planMode, files, onSubmit],
  );

  /* Keyboard */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void handleSubmit(false);
    }
  };

  /* Suggestion click: prefill + focus, do NOT submit */
  const handleSuggestionClick = (suggestion: string) => {
    setValue(suggestion);
    requestAnimationFrame(() => inputRef.current?.focus());
  };

  /* Build button label */
  const buildLabel = planMode ? "Plan first" : "Build";
  const buildIcon  = planMode
    ? <ClipboardList className="w-5 h-5" aria-hidden />
    : <ArrowRight    className="w-5 h-5" aria-hidden />;

  /* Placeholder shown in the actual input element. When typing-cycle is
     active and there's no value, we show the cycling text. Otherwise we
     show a static fallback so screen-reader / assistive tech users still
     get useful guidance. */
  const placeholder = hasValue
    ? ""
    : typewriter || `${PLACEHOLDER_PREFIX}…`;

  return (
    <div className="flex flex-col gap-3 w-full">
      {/* Hidden file input — image only, multi-select. */}
      <input
        ref={fileInputRef}
        type="file"
        accept={ACCEPT_MIME}
        multiple
        className="sr-only"
        onChange={(e) => handleFilesChosen(e.target.files)}
        aria-hidden
        tabIndex={-1}
      />

      {/* ---- Card ---- */}
      <div
        className={cn(
          "relative rounded-2xl",
          isDisabled && "opacity-60 pointer-events-none",
        )}
      >
        {/* Animated gradient border (absolute, behind card surface) */}
        <div
          className={cn("detective-focus-ring rounded-2xl")}
          aria-hidden
        />

        {/* Card surface. Phase 43.16: border removed (Marc reported the
            outline made the bar feel small). The animated gradient
            focus-ring (above) + the soft shadow now do all the
            outlining work. */}
        <div
          className={cn(
            "relative z-10 rounded-2xl bg-white",
            "shadow-[0_8px_40px_rgba(0,0,0,0.06)]",
            "transition-shadow duration-300",
            focused && "shadow-[0_12px_48px_rgba(0,0,0,0.10)]",
          )}
        >
          {/* ---- Row 1 — input only, full-bleed.
                 Phase 40k (2026-05-21) — Marc's call: toggle buttons
                 were eating horizontal space, cutting the typewriter
                 placeholder mid-word. Input now gets the whole row to
                 itself; secondary actions live in a toolbar below. */}
          <div className="px-5 pt-5 pb-3 sm:px-7 sm:pt-6 sm:pb-3">
            <input
              ref={inputRef}
              type="text"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => setFocused(true)}
              onBlur={() => setFocused(false)}
              placeholder={placeholder}
              disabled={isDisabled}
              autoFocus={autoFocus}
              className={cn(
                "w-full bg-transparent border-none outline-none focus:outline-none",
                // Phase 40l — Marc's call: bumped down a notch from
                // text-xl/2xl so the typewriter prompts read comfortably
                // without dominating the card.
                "text-base sm:text-lg text-foreground placeholder:text-muted-foreground",
                "leading-snug",
              )}
              aria-label="Describe your business or enter your website"
            />
          </div>

          {/* ---- Row 2 — toolbar (toggle buttons left, Build right).
                 Sits at the bottom of the card. The Build button stays
                 the primary visual anchor; mic, paperclip, Plan are
                 secondary affordances that don't compete with the
                 typewriter prompt above. */}
          <div className="flex items-center gap-2 px-3 pb-3 pt-1 sm:px-4 sm:pb-4">
            {/* Mic — only if Web Speech API is supported. */}
            {speechSupported && (
              <button
                type="button"
                onClick={listening ? stopListening : startListening}
                disabled={isDisabled}
                aria-pressed={listening}
                aria-label={listening ? "Stop dictation" : "Dictate your idea"}
                title={listening ? "Stop dictation" : "Dictate your idea"}
                className={cn(
                  "shrink-0 flex items-center justify-center w-10 h-10 rounded-full",
                  "text-muted-foreground hover:text-foreground",
                  "hover:bg-accent transition-colors duration-150",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                  listening && "bg-red-50 text-red-600 hover:text-red-700 hover:bg-red-100 detective-mic-recording",
                )}
              >
                {listening ? <Square className="w-4 h-4" /> : <Mic className="w-5 h-5" />}
              </button>
            )}

            {/* File attach — with lock state for signed-out visitors. */}
            <div
              className="relative shrink-0"
              onMouseEnter={() => attachLocked && setShowLockTip(true)}
              onMouseLeave={() => {
                if (!attachLocked) return;
                if (lockTipTimer.current) clearTimeout(lockTipTimer.current);
                setShowLockTip(false);
              }}
            >
              <button
                type="button"
                onClick={handleFilePick}
                disabled={isDisabled || (!attachLocked && files.length >= MAX_FILES)}
                aria-label={attachLocked ? "Sign in to attach files" : "Attach inspiration images"}
                title={attachLocked
                  ? "This feature unlocks after signing in."
                  : "Attach images (logo, references, photos of your space)"}
                className={cn(
                  "flex items-center justify-center w-10 h-10 rounded-full relative",
                  "text-muted-foreground hover:text-foreground",
                  "hover:bg-accent transition-colors duration-150",
                  "disabled:opacity-40 disabled:cursor-not-allowed",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                  attachLocked && "opacity-70",
                )}
              >
                <Paperclip className="w-5 h-5" />
                {attachLocked && (
                  <span
                    aria-hidden
                    className="absolute -bottom-0.5 -right-0.5 inline-flex items-center justify-center w-4 h-4 rounded-full bg-foreground text-background"
                  >
                    <Lock className="w-2.5 h-2.5" strokeWidth={3} />
                  </span>
                )}
              </button>

              {/* Phase 43.16 — lock tooltip. Pops above the button on
                  hover OR after click. White card with small caret. */}
              <AnimatePresence>
                {attachLocked && showLockTip && (
                  <motion.div
                    initial={{ opacity: 0, y: 4, scale: 0.96 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 4, scale: 0.96 }}
                    transition={{ duration: 0.18, ease: EASE_CINEMATIC }}
                    role="tooltip"
                    className={cn(
                      "absolute z-50 left-1/2 -translate-x-1/2 bottom-full mb-2",
                      "px-3 py-2 rounded-lg bg-foreground text-background",
                      "text-xs font-semibold whitespace-nowrap",
                      "shadow-[0_8px_24px_rgba(0,0,0,0.18)]",
                    )}
                  >
                    <Lock className="w-3 h-3 inline-block mr-1.5 -mt-0.5" strokeWidth={3} />
                    This feature unlocks after signing in.
                    {/* Caret pointing down */}
                    <span
                      aria-hidden
                      className="absolute top-full left-1/2 -translate-x-1/2 -mt-px w-2 h-2 bg-foreground rotate-45"
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Plan-mode toggle */}
            <button
              type="button"
              onClick={() => setPlanMode((p) => !p)}
              disabled={isDisabled}
              aria-pressed={planMode}
              title={planMode
                ? "Plan first — we'll show you the 7-field site plan before spending a build credit"
                : "Plan first — preview the build plan instead of generating"}
              className={cn(
                "shrink-0 inline-flex items-center gap-1.5 rounded-full px-3 h-10",
                "text-sm font-medium transition-colors duration-150",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                planMode
                  ? "bg-foreground/10 text-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent",
              )}
            >
              <ClipboardList className="w-4 h-4" aria-hidden />
              <span>Plan</span>
            </button>

            {/* Spacer pushes Build to the right edge */}
            <div className="flex-1" aria-hidden />

            {/* Build CTA — glows once the value is unlocked */}
            <button
              type="button"
              onClick={() => void handleSubmit(false)}
              disabled={isDisabled || !hasValue}
              className={cn(
                "shrink-0 flex items-center gap-1.5 rounded-full px-5 sm:px-6 h-10 sm:h-11",
                "bg-foreground text-background text-base font-semibold",
                "transition-all duration-200",
                "hover:opacity-90 active:scale-95",
                "disabled:opacity-40 disabled:cursor-not-allowed",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                hasValue && !isDisabled && "detective-send-glow",
              )}
            >
              {submitting ? (
                <span className={cn(type.body.s, "opacity-70")}>…</span>
              ) : (
                <>
                  <span>{buildLabel}</span>
                  {buildIcon}
                </>
              )}
            </button>
          </div>

          {/* File rail — thumbnails of attached images */}
          <AnimatePresence>
            {files.length > 0 && (
              <motion.div
                key="files-rail"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.25, ease: EASE_CINEMATIC }}
                className="overflow-hidden"
              >
                <div className="px-5 pb-3 flex flex-wrap gap-2">
                  {files.map((f, i) => {
                    const url = URL.createObjectURL(f);
                    return (
                      <div
                        key={`${f.name}-${i}`}
                        className="relative group flex items-center gap-2 pl-1 pr-2 py-1 rounded-full bg-muted border border-border max-w-[220px]"
                      >
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={url}
                          alt=""
                          className="w-7 h-7 rounded-full object-cover shrink-0"
                          onLoad={() => URL.revokeObjectURL(url)}
                        />
                        <span className="text-xs text-foreground/85 truncate">{f.name}</span>
                        <button
                          type="button"
                          onClick={() => removeFile(i)}
                          aria-label={`Remove ${f.name}`}
                          className="shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-foreground/5"
                        >
                          <X className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    );
                  })}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* File error — inline, dismisses on next successful add */}
          {fileError && (
            <div className="px-5 pb-3 text-xs text-destructive">{fileError}</div>
          )}

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
                <div className="px-5 pb-4 flex flex-col gap-1.5">
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

                  {/* Plan-mode hint */}
                  {planMode && (
                    <div className="flex items-center gap-2 text-[13px] text-foreground/75 pl-5">
                      <ClipboardList className="w-3.5 h-3.5" aria-hidden />
                      <span>Plan-first mode on — we'll preview the build plan before spending a credit.</span>
                    </div>
                  )}

                  {/* URL-only: inspire link */}
                  {isUrl && (
                    <motion.div
                      initial={{ opacity: 0, x: -4 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -4 }}
                      transition={{ duration: 0.22, ease: EASE_CINEMATIC, delay: 0.08 }}
                      className="pl-5"
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
                        ↳ Switch to &quot;Inspired by this design&quot; mode
                      </button>
                    </motion.div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* ---- Rotating suggestion pill (below the card) ---- */}
      {/* Phase 40m (2026-05-21) — Marc's call: the rotating suggestion
          is now a proper carousel pill (not just underlined text).
          Reads as an obvious clickable affordance + carries its own
          visual weight against the cream page background. The pill
          itself swaps every 4s via AnimatePresence; the wrapper row
          (the "Can't think of anything?" label + pill slot) only
          animates in/out when the user starts/clears typing. */}
      <AnimatePresence mode="wait">
        {!hasValue && (
          <motion.div
            key="rotating-row"
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 4 }}
            transition={{ duration: 0.25, ease: EASE_CINEMATIC }}
            className="flex items-center gap-3 px-1 min-h-[44px] flex-wrap"
          >
            <span className={cn(type.caption, "shrink-0")}>
              Can&apos;t think of anything? Give these a try:
            </span>
            {/* Slot keeps a stable position while the pill inside swaps */}
            <span className="relative inline-flex items-center">
              <AnimatePresence mode="wait">
                <motion.button
                  key={rotating.idx}
                  type="button"
                  onClick={() => handleSuggestionClick(rotating.suggestion)}
                  initial={{ opacity: 0, y: 8, scale: 0.96 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -8, scale: 0.96 }}
                  transition={{ duration: 0.45, ease: EASE_CINEMATIC }}
                  className={cn(
                    "inline-flex items-center gap-2 px-4 py-1.5 rounded-full",
                    "bg-white border border-border/70 shadow-[0_2px_12px_rgba(0,0,0,0.04)]",
                    "text-[13px] font-medium text-foreground/85 whitespace-nowrap",
                    "hover:bg-white hover:text-foreground hover:border-foreground/25",
                    "hover:shadow-[0_4px_18px_rgba(0,0,0,0.08)]",
                    "transition-[colors,shadow,border] duration-200",
                    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                  )}
                >
                  {rotating.suggestion}
                </motion.button>
              </AnimatePresence>
            </span>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default DetectiveInput;
