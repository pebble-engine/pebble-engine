"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence, MotionConfig } from "framer-motion";
import {
  HelpCircle,
  Home,
  Plane,
  Briefcase,
  Users,
  Star,
  MoreHorizontal,
  BookOpen,
  Mail,
  CalendarDays,
  ShoppingBag,
  Image as ImageIcon,
  CreditCard,
  Sun,
  Award,
  Zap,
  Wind,
  PartyPopper,
  Gem,
  ArrowRight,
  Check,
  Pencil,
  type LucideIcon,
} from "lucide-react";
import { LanguagePicker } from "@/components/language-picker";
import { patchBrief, guessIndustryFromIdea, getBrief } from "@/lib/state";
import { STANDARD_S, SHORT_S, EASE_CINEMATIC, EASE_QUIET } from "@/lib/motion";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";

/**
 * Idea phase — the chip-driven clarifying questions that used to live
 * at /intake. Three steps in one panel (audience → site_functions →
 * brand_tone) + a freeform notes textarea + the language picker.
 *
 * Lives inside the unified workspace shell. On "Continue" from the
 * last step, calls ``onAdvance()`` to push the URL hash to
 * ``#phase=plan``; the shell renders the plan phase next.
 */

type Step = {
  key: "audience" | "site_functions" | "brand_tone";
  multi: boolean;
  headline: string;
  subhead: string;
  tip: string;
  chips: { id: string; label: string; Icon: LucideIcon }[];
};

const STEPS: Step[] = [
  {
    key: "audience",
    multi: true,
    headline: "Who walks in your door?",
    subhead: "Don't overthink it — locals, tourists, professionals, whoever you serve.",
    tip: "We use this to pick who the homepage talks to first. Mixing two audiences is fine; mixing five usually waters down every page. Aim for one or two.",
    chips: [
      { id: "locals",        label: "Locals",        Icon: Home },
      { id: "travelers",     label: "Travelers",     Icon: Plane },
      { id: "professionals", label: "Professionals", Icon: Briefcase },
      { id: "families",      label: "Families",      Icon: Users },
      { id: "enthusiasts",   label: "Enthusiasts",   Icon: Star },
      { id: "other",         label: "Other",         Icon: MoreHorizontal },
    ],
  },
  {
    key: "site_functions",
    multi: true,
    headline: "What's the main thing visitors should do?",
    subhead: "Pick what matters. Pebble adds the right page for each.",
    tip: "Each pick adds a corresponding section or page — Book becomes a booking widget, Buy becomes a product grid. You can edit or remove any of them later in the workspace.",
    chips: [
      { id: "presence",  label: "See your story",      Icon: BookOpen },
      { id: "leads",     label: "Get in touch",        Icon: Mail },
      { id: "booking",   label: "Book an appointment", Icon: CalendarDays },
      { id: "ecommerce", label: "Buy something",       Icon: ShoppingBag },
      { id: "portfolio", label: "See your work",       Icon: ImageIcon },
      { id: "payment",   label: "Pay or donate",       Icon: CreditCard },
    ],
  },
  {
    key: "brand_tone",
    multi: false,
    headline: "What feeling should it give off?",
    subhead: "One word that captures the mood.",
    tip: "Tone steers the design DNA: a bold tone biases toward Brutalist Editorial or Cinematic IMAX; a calm tone toward Swiss Magazine or Whitespace Maximum. You can regenerate to try a different DNA later.",
    chips: [
      { id: "warm",         label: "Warm",         Icon: Sun },
      { id: "professional", label: "Professional", Icon: Award },
      { id: "bold",         label: "Bold",         Icon: Zap },
      { id: "calm",         label: "Calm",         Icon: Wind },
      { id: "playful",      label: "Playful",      Icon: PartyPopper },
      { id: "premium",      label: "Premium",      Icon: Gem },
    ],
  },
];

type Props = {
  onAdvance: () => void;
};

// ---------------------------------------------------------------------------
// Label maps for the confirmation card — chip id → human label.
// ---------------------------------------------------------------------------

const AUDIENCE_LABELS: Record<string, string> = {
  locals:        "Locals",
  travelers:     "Travelers",
  professionals: "Professionals",
  families:      "Families",
  enthusiasts:   "Enthusiasts",
  other:         "Other",
};

const FUNCTION_LABELS: Record<string, string> = {
  presence:  "See your story",
  leads:     "Get in touch",
  booking:   "Book an appointment",
  ecommerce: "Buy something",
  portfolio: "See your work",
  payment:   "Pay or donate",
};

const TONE_LABELS: Record<string, string> = {
  warm:         "Warm",
  professional: "Professional",
  bold:         "Bold",
  calm:         "Calm",
  playful:      "Playful",
  premium:      "Premium",
};

// ---------------------------------------------------------------------------
// SmartDefaults confirmation card — shown when the brief is pre-filled.
// ---------------------------------------------------------------------------

function ConfirmationCard({
  audience,
  siteFunctions,
  brandTone,
  onConfirm,
  onEdit,
}: {
  audience:      string[];
  siteFunctions: string[];
  brandTone:     string;
  onConfirm:     () => void;
  onEdit:        () => void;
}) {
  return (
    <MotionConfig reducedMotion="user">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -16 }}
        transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
        className="flex flex-col h-full"
      >
        <main className="flex-grow flex flex-col items-center justify-center px-4 md:px-8 py-8">
          <div className="max-w-xl w-full space-y-8">
            {/* Header */}
            <div className="text-center space-y-2">
              <h1 className={`${type.heading.l} text-foreground`}>Here&apos;s what I figured out</h1>
              <p className={`${type.body.m} text-muted-foreground`}>
                Edit anything if it&apos;s off.
              </p>
            </div>

            {/* Confirmation card */}
            <div className="rounded-2xl bg-card border border-border p-6 space-y-6 shadow-[var(--shadow-1)]">
              {/* Audience */}
              <div className="space-y-2">
                <p className={`${type.eyebrow}`}>Audience</p>
                <div className="flex flex-wrap gap-2">
                  {audience.map((id) => (
                    <span
                      key={id}
                      className={`${type.badge} px-3 py-1 rounded-full bg-primary/10 text-primary border border-primary/20`}
                    >
                      {AUDIENCE_LABELS[id] ?? id}
                    </span>
                  ))}
                </div>
              </div>

              {/* Site functions */}
              <div className="space-y-2">
                <p className={`${type.eyebrow}`}>Visitors will&hellip;</p>
                <div className="flex flex-wrap gap-2">
                  {siteFunctions.map((id) => (
                    <span
                      key={id}
                      className={`${type.badge} px-3 py-1 rounded-full bg-primary/10 text-primary border border-primary/20`}
                    >
                      {FUNCTION_LABELS[id] ?? id}
                    </span>
                  ))}
                </div>
              </div>

              {/* Brand tone */}
              <div className="space-y-2">
                <p className={`${type.eyebrow}`}>Tone</p>
                <span
                  className={`${type.badge} inline-block px-3 py-1 rounded-full bg-primary/10 text-primary border border-primary/20`}
                >
                  {TONE_LABELS[brandTone] ?? brandTone}
                </span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex flex-col gap-3">
              <motion.button
                whileTap={{ scale: 0.97 }}
                onClick={onConfirm}
                className={`${interactions.button} w-full flex items-center justify-center gap-2 bg-primary text-primary-foreground px-8 py-3 rounded-lg shadow-md ${type.label}`}
              >
                Looks good <ArrowRight className="w-4 h-4" />
              </motion.button>
              <button
                type="button"
                onClick={onEdit}
                className={`${interactions.chip} w-full flex items-center justify-center gap-2 text-muted-foreground hover:text-foreground py-2 ${type.label}`}
              >
                <Pencil className="w-3.5 h-3.5" aria-hidden />
                Change anything?
              </button>
            </div>
          </div>
        </main>
      </motion.div>
    </MotionConfig>
  );
}

// ---------------------------------------------------------------------------

export function IdeaPhase({ onAdvance }: Props) {
  const [stepIdx, setStepIdx] = useState(0);
  const step = STEPS[stepIdx];
  const [validationError, setValidationError] = useState<string | null>(null);

  // Per-step selections — read once from saved brief, mutated locally.
  const brief = getBrief();

  // Phase 37 — confirmation card: shown when smart-defaults pre-filled the brief.
  // Flip to false when the user clicks "Change anything?" to reveal the full
  // 3-step questionnaire. Stays true across re-renders (local state).
  const prefilled =
    Array.isArray(brief.audience) && (brief.audience as string[]).length > 0 &&
    Array.isArray(brief.site_functions) && (brief.site_functions as string[]).length > 0 &&
    typeof brief.brand_tone === "string" && (brief.brand_tone as string).length > 0;
  const [collapsed, setCollapsed] = useState(prefilled);
  const [selections, setSelections] = useState<Record<string, Set<string>>>(() => {
    const init: Record<string, Set<string>> = {};
    for (const s of STEPS) {
      const existing = brief[s.key];
      if (Array.isArray(existing)) init[s.key] = new Set(existing);
      else if (typeof existing === "string" && existing) init[s.key] = new Set([existing]);
      else init[s.key] = new Set();
    }
    return init;
  });

  const toggleChip = (chipId: string) => {
    setValidationError(null);
    setSelections((prev) => {
      const next = { ...prev };
      const set = new Set(next[step.key]);
      if (step.multi) {
        if (set.has(chipId)) set.delete(chipId);
        else set.add(chipId);
      } else {
        set.clear();
        set.add(chipId);
      }
      next[step.key] = set;
      patchBrief({
        [step.key]: step.multi ? Array.from(set) : Array.from(set)[0] || "",
      });
      return next;
    });
  };

  const handleBack = () => {
    if (stepIdx > 0) setStepIdx(stepIdx - 1);
  };

  const handleContinue = () => {
    if (selected.size === 0) {
      setValidationError("Please select at least one option to continue.");
      return;
    }
    setValidationError(null);
    if (stepIdx < STEPS.length - 1) {
      setStepIdx(stepIdx + 1);
      return;
    }
    // Final step — derive a guess at business_type from the idea text, then advance.
    const idea = (brief.extra_context as string) || "";
    if (!brief.business_type) patchBrief({ business_type: guessIndustryFromIdea(idea) });
    onAdvance();
  };

  const selected = selections[step.key];

  // Phase 37 — render the confirmation card when smart-defaults are present
  // and the user hasn't opted to edit manually.
  if (collapsed && prefilled) {
    return (
      <AnimatePresence mode="wait">
        <ConfirmationCard
          key="confirmation"
          audience={brief.audience as string[]}
          siteFunctions={brief.site_functions as string[]}
          brandTone={brief.brand_tone as string}
          onConfirm={() => {
            // Ensure business_type is guessed if not already set.
            const idea = (brief.extra_context as string) || "";
            if (!brief.business_type) patchBrief({ business_type: guessIndustryFromIdea(idea) });
            onAdvance();
          }}
          onEdit={() => setCollapsed(false)}
        />
      </AnimatePresence>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* 2026-05-19: DnaPreview pill removed from Idea phase. The DNA is
          decided silently by the engine from brief + creative_direction +
          industry affinity; the user's first deliberate look at the chosen
          style is on the Plan phase ("Visual style" card). Marc: "Minimal
          distractions — no try-another button pulling people away from
          the current question." */}

      <div className="flex justify-center pt-6">
        <div className="flex gap-3" role="status" aria-label={`Step ${stepIdx + 1} of ${STEPS.length}`}>
          <span className="sr-only">Step {stepIdx + 1} of {STEPS.length}</span>
          {STEPS.map((_, i) => (
            <motion.div
              key={i}
              className="h-3 rounded-full"
              initial={false}
              animate={{
                width: i === stepIdx ? 32 : 12,
                backgroundColor:
                  i < stepIdx
                    ? "var(--color-sage)"
                    : i === stepIdx
                      ? "var(--color-river)"
                      : "var(--color-pebble)",
              }}
              transition={{ duration: STANDARD_S, ease: EASE_QUIET }}
            />
          ))}
        </div>
      </div>

      <main className="flex-grow flex flex-col items-center justify-center px-4 md:px-8 py-8">
        <div className="max-w-3xl w-full">
          <AnimatePresence mode="wait">
            <motion.div
              key={step.key}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: STANDARD_S, ease: EASE_QUIET }}
              className="space-y-10 text-center"
            >
              <div className="space-y-3">
                <p className={`${type.mono} text-muted-foreground`}>
                  Question {stepIdx + 1} of {STEPS.length}
                </p>
                <h1 className={`${type.display.l} text-foreground inline-flex items-center gap-2 justify-center`}>
                  {step.headline}
                  <Tooltip text={step.tip} />
                </h1>
                <p className={`${type.body.m} text-muted-foreground max-w-xl mx-auto`}>{step.subhead}</p>
              </div>

              <motion.div
                className="grid grid-cols-2 md:grid-cols-3 gap-3"
                initial="hidden"
                animate="visible"
                variants={{
                  hidden: {},
                  visible: { transition: { staggerChildren: 0.06 } },
                }}
              >
                {step.chips.map((chip) => {
                  const isSelected = selected.has(chip.id);
                  return (
                    <motion.button
                      key={chip.id}
                      variants={{
                        hidden: { opacity: 0, y: 16 },
                        visible: { opacity: 1, y: 0, transition: { duration: STANDARD_S, ease: EASE_CINEMATIC } },
                      }}
                      onClick={() => toggleChip(chip.id)}
                      whileTap={{ scale: 0.98 }}
                      whileHover={{ y: -2 }}
                      transition={{ duration: 0.18, ease: EASE_QUIET }}
                      className={`group relative flex flex-col items-start justify-end gap-5 p-5 min-h-[140px] rounded-lg overflow-hidden transition-colors duration-200 ${
                        isSelected
                          ? "bg-primary/10 ring-2 ring-foreground text-foreground"
                          : "bg-transparent ring-1 ring-border hover:ring-foreground/40 text-foreground"
                      }`}
                    >
                      {/* Check mark overlay — top-right corner when selected. */}
                      {isSelected && (
                        <Check className="absolute top-2 right-2 w-3.5 h-3.5 text-primary" aria-hidden />
                      )}

                      {/* Top-left icon — small, restrained. Becomes brighter when selected. */}
                      <chip.Icon
                        className={`w-5 h-5 transition-colors duration-200 ${
                          isSelected ? "text-foreground" : "text-muted-foreground group-hover:text-foreground/80"
                        }`}
                        aria-hidden
                      />

                      {/* Label — bottom-left, deliberate weight, left-aligned reads more editorial. */}
                      <span className={`${type.heading.s} text-left leading-tight`}>
                        {chip.label}
                      </span>

                      {/* Selection indicator: a hairline accent on the LEFT edge,
                          not a badge in the corner. Reads as "this is committed"
                          rather than "this is a form input." */}
                      <AnimatePresence>
                        {isSelected && (
                          <motion.span
                            initial={{ scaleY: 0, opacity: 0 }}
                            animate={{ scaleY: 1, opacity: 1 }}
                            exit={{ scaleY: 0, opacity: 0 }}
                            transition={{ duration: SHORT_S, ease: EASE_CINEMATIC }}
                            className="absolute left-0 top-3 bottom-3 w-[2px] bg-foreground rounded-full origin-center"
                            aria-hidden
                          />
                        )}
                      </AnimatePresence>
                    </motion.button>
                  );
                })}
              </motion.div>

              {validationError && (
                <p className={`${type.body.s} text-destructive text-center mt-3`}>{validationError}</p>
              )}
            </motion.div>
          </AnimatePresence>

          <div className="mt-10 max-w-2xl mx-auto space-y-5">
            {/* Creative direction — free-text aesthetic hint. Shapes the
                Layout DNA pick (keyword-classified server-side) AND gets
                injected as the top-priority block in the build prompt.
                Placeholder examples lean PLAIN-ENGLISH on purpose — most
                Pebble users don't speak designer ("editorial magazine
                spread" is opaque). Use feeling-based examples that map
                to real businesses the user already knows. */}
            <div>
              <label htmlFor="creative_direction" className={`block ${type.label} text-muted-foreground mb-2`}>
                How should your site feel? <span className="text-muted-foreground/60">(optional)</span>
              </label>
              <textarea
                id="creative_direction"
                defaultValue={(brief.creative_direction as string) || ""}
                onBlur={(e) => patchBrief({ creative_direction: e.target.value.trim().slice(0, 500) })}
                placeholder="e.g. warm and friendly, like a neighborhood cafe"
                rows={2}
                maxLength={500}
                className="w-full bg-card border border-border rounded-xl px-4 py-3 text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-ring resize-none"
              />
            </div>

            <div>
              <label htmlFor="notes_freeform" className={`block ${type.label} text-muted-foreground mb-2`}>
                Anything else we should know? <span className="text-muted-foreground/60">(optional)</span>
              </label>
              <textarea
                id="notes_freeform"
                defaultValue={(brief.notes_freeform as string) || ""}
                onBlur={(e) => patchBrief({ notes_freeform: e.target.value })}
                placeholder="Example: your business hours, brand colors you already use, a website you love, things you want to avoid. Whatever helps."
                rows={3}
                className="w-full bg-card border border-border rounded-xl px-4 py-3 text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-ring resize-none"
              />
              <LanguagePicker />
            </div>
          </div>
        </div>
      </main>

      <footer className="w-full px-8 py-6 flex justify-between items-center">
        <button
          onClick={handleBack}
          disabled={stepIdx === 0}
          className={`${interactions.chip} flex items-center gap-1 text-muted-foreground hover:text-foreground disabled:opacity-40 disabled:cursor-not-allowed px-3 py-2 rounded-md`}
        >
          <span className={type.label}>Back</span>
        </button>
        <motion.button
          whileTap={{ scale: 0.97 }}
          onClick={handleContinue}
          className={`${interactions.button} flex items-center gap-2 bg-primary text-primary-foreground px-8 py-3 rounded-lg shadow-md ${type.label}`}
        >
          {stepIdx === STEPS.length - 1 ? "Generate plan" : "Continue"}
          <ArrowRight className="w-4 h-4" />
        </motion.button>
      </footer>
    </div>
  );
}

function Tooltip({ text }: { text: string }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLSpanElement>(null);
  useEffect(() => {
    if (!open) return;
    function onClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    window.addEventListener("click", onClick);
    return () => window.removeEventListener("click", onClick);
  }, [open]);

  return (
    <span ref={ref} className="relative inline-flex items-center align-middle">
      <button
        type="button"
        onClick={(e) => { e.stopPropagation(); setOpen((v) => !v); }}
        className={`${interactions.iconButton} w-7 h-7 rounded-full text-muted-foreground hover:text-foreground inline-flex items-center justify-center`}
        aria-label="What does this question mean?"
        aria-expanded={open}
      >
        <HelpCircle className="w-5 h-5" />
      </button>
      {open && (
        <span
          role="tooltip"
          className="absolute z-30 top-full mt-2 left-1/2 -translate-x-1/2 w-72 max-w-[80vw] bg-card border border-border rounded-xl px-4 py-3 text-sm text-muted-foreground shadow-[var(--shadow-1)] text-left leading-snug font-sans"
        >
          {text}
        </span>
      )}
    </span>
  );
}
