"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ChevronLeft,
  ArrowRight,
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
  type LucideIcon,
} from "lucide-react";
import { TopNav } from "@/components/top-nav";
import { patchBrief, guessIndustryFromIdea, getBrief } from "@/lib/state";

type Step = {
  key: "audience" | "site_functions" | "brand_tone";
  multi: boolean;
  headline: string;
  subhead: string;
  chips: { id: string; label: string; Icon: LucideIcon }[];
};

const STEPS: Step[] = [
  {
    key: "audience",
    multi: true,
    headline: "Who walks in your door?",
    subhead: "Don't overthink it — locals, tourists, professionals, whoever you serve.",
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

export default function IntakePage() {
  const router = useRouter();
  const [stepIdx, setStepIdx] = useState(0);
  const step = STEPS[stepIdx];

  // Per-step selections — read once from saved brief, mutated locally.
  const brief = getBrief();
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
    else router.push("/");
  };

  const handleContinue = () => {
    if (stepIdx < STEPS.length - 1) {
      setStepIdx(stepIdx + 1);
      return;
    }
    // Final step — derive a guess at business_type from the idea text, then go to thinking.
    const idea = (brief.extra_context as string) || "";
    if (!brief.business_type) patchBrief({ business_type: guessIndustryFromIdea(idea) });
    router.push("/thinking");
  };

  const selected = selections[step.key];

  return (
    <div className="min-h-screen flex flex-col">
      <TopNav rightSlot={
        <button
          onClick={() => router.push("/thinking")}
          className="text-sm font-semibold text-muted-foreground hover:text-foreground transition-colors px-3 py-1.5 rounded-md hover:bg-accent"
        >
          Skip for now
        </button>
      } />

      {/* Progress dots */}
      <div className="flex justify-center pt-8">
        <div className="flex gap-3">
          {STEPS.map((_, i) => (
            <motion.div
              key={i}
              className="h-2 rounded-full"
              initial={false}
              animate={{
                width: i === stepIdx ? 32 : 8,
                backgroundColor:
                  i < stepIdx
                    ? "var(--color-sage)"
                    : i === stepIdx
                      ? "var(--color-river)"
                      : "var(--color-pebble)",
              }}
              transition={{ duration: 0.35, ease: [0.4, 0, 0.2, 1] }}
            />
          ))}
        </div>
      </div>

      <main className="flex-grow flex flex-col items-center justify-center px-4 md:px-8 py-12">
        <div className="max-w-3xl w-full">
          <AnimatePresence mode="wait">
            <motion.div
              key={step.key}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.35, ease: [0.4, 0, 0.2, 1] }}
              className="space-y-12 text-center"
            >
              <div className="space-y-3">
                <h1 className="font-display text-4xl md:text-5xl font-bold tracking-tight text-foreground">
                  {step.headline}
                </h1>
                <p className="text-lg text-muted-foreground max-w-xl mx-auto">{step.subhead}</p>
              </div>

              <motion.div
                className="grid grid-cols-2 md:grid-cols-3 gap-4"
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
                        visible: { opacity: 1, y: 0 },
                      }}
                      onClick={() => toggleChip(chip.id)}
                      whileTap={{ scale: 0.96 }}
                      className={`relative flex flex-col items-center justify-center gap-3 p-6 rounded-xl transition-colors ${
                        isSelected
                          ? "bg-secondary/15 border border-secondary text-foreground"
                          : "bg-card border border-border hover:bg-accent text-foreground"
                      }`}
                    >
                      <chip.Icon className={`w-6 h-6 ${isSelected ? "text-secondary" : "text-muted-foreground"}`} />
                      <span className="text-sm font-semibold">{chip.label}</span>
                      <AnimatePresence>
                        {isSelected && (
                          <motion.span
                            initial={{ scale: 0, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0, opacity: 0 }}
                            className="absolute top-2 right-2 w-5 h-5 bg-secondary rounded-full flex items-center justify-center text-xs text-white"
                          >
                            ✓
                          </motion.span>
                        )}
                      </AnimatePresence>
                    </motion.button>
                  );
                })}
              </motion.div>
            </motion.div>
          </AnimatePresence>
        </div>
      </main>

      <footer className="w-full px-8 py-8 flex justify-between items-center">
        <button
          onClick={handleBack}
          className="flex items-center gap-1 text-muted-foreground hover:text-foreground transition-colors px-3 py-2 rounded-md hover:bg-accent"
        >
          <ChevronLeft className="w-5 h-5" />
          <span className="text-sm font-semibold">Back</span>
        </button>
        <motion.button
          whileTap={{ scale: 0.97 }}
          onClick={handleContinue}
          className="flex items-center gap-2 bg-primary text-primary-foreground px-8 py-3 rounded-lg text-sm font-semibold shadow-md hover:opacity-90 transition-opacity"
        >
          {stepIdx === STEPS.length - 1 ? "Generate plan" : "Continue"}
          <ArrowRight className="w-4 h-4" />
        </motion.button>
      </footer>
    </div>
  );
}
