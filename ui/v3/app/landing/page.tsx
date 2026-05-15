"use client";

/**
 * Marketing landing page (/landing) — what someone sees when they first hear
 * about Pebble. Separate from `/` which is the app's questionnaire entry.
 *
 * The page is designed to be honest: every feature shown below corresponds to
 * something that actually ships in this repo today. The "coming soon" strip
 * holds the placeholders so visitors don't get hooked on a promise we don't
 * keep yet.
 */

import { useState } from "react";
import Link from "next/link";
import { motion, useReducedMotion } from "framer-motion";
import { ThemeToggle } from "@/components/theme-toggle";
import { AuthMenu } from "@/components/auth-menu";
import { ArrowRight, Check, ChevronDown, History, Image as ImageIcon, MousePointerClick, Shield, Sparkles, Wand2 } from "lucide-react";
import { PUBLIC_FAQ as FAQ_ITEMS } from "@/lib/faq";

/* ------------------------------------------------------------------ Hero -- */

function Hero() {
  const reduce = useReducedMotion();
  return (
    <section className="relative overflow-hidden border-b border-border bg-background">
      <div className="absolute inset-0 -z-10 opacity-60 [background-image:radial-gradient(var(--color-pebble)_1px,transparent_1px)] [background-size:24px_24px] dark:opacity-20" />

      <div className="mx-auto max-w-6xl px-6 pt-32 pb-24 md:pt-40 md:pb-32">
        <motion.div
          initial={reduce ? false : { opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          className="space-y-8 text-center md:text-left"
        >
          <span className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1 text-xs font-medium tracking-wide text-muted-foreground">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-60" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-primary" />
            </span>
            Free preview — no card required
          </span>

          <h1 className="font-display text-5xl md:text-7xl font-bold tracking-tight leading-[1.05] text-foreground">
            A website built for your business —<br className="hidden md:block" />
            <span className="text-primary">not picked from a gallery.</span>
          </h1>

          <p className="max-w-2xl text-lg md:text-xl text-muted-foreground leading-relaxed">
            Tell Pebble what you do. It synthesizes a site from a fresh design DNA every time
            — different fonts, layout posture, and signature moves on every build. No two
            Pebbles look alike, even for the same business.
          </p>

          <div className="flex flex-col md:flex-row items-center gap-3 md:gap-4 pt-2">
            <Link
              href="/workspace#phase=idea"
              className="group inline-flex items-center gap-2 rounded-full bg-primary px-7 py-3.5 text-base font-medium text-primary-foreground shadow-[var(--shadow-1)] transition-transform hover:scale-[1.02] active:scale-[0.98]"
            >
              Start building — it's free
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
            <Link
              href="/migrate"
              className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-7 py-3.5 text-base font-medium text-foreground hover:bg-accent transition-colors"
            >
              Migrate from an existing site
            </Link>
          </div>

          <div className="flex flex-wrap items-center gap-x-6 gap-y-2 pt-4 text-sm text-muted-foreground">
            <span className="inline-flex items-center gap-1.5">
              <Check className="h-4 w-4 text-primary" /> 10-minute first build
            </span>
            <span className="inline-flex items-center gap-1.5">
              <Check className="h-4 w-4 text-primary" /> Real undo on every edit
            </span>
            <span className="inline-flex items-center gap-1.5">
              <Check className="h-4 w-4 text-primary" /> Zero third-party trackers
            </span>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

/* ----------------------------------------------------- DNA Differentiator -- */

const DNA_VARIANTS = [
  { id: "warm",   label: "Warm + handmade", swatches: ["#c76e3a", "#f7f3ec", "#5b6f4a"], font: "font-display italic" },
  { id: "clean",  label: "Clean + modern",  swatches: ["#205661", "#ece6dc", "#1f1d1a"], font: "font-sans tracking-tight" },
  { id: "bold",   label: "Bold + editorial", swatches: ["#1f1d1a", "#f7f3ec", "#c76e3a"], font: "font-display uppercase tracking-wider" },
];

function Differentiator() {
  return (
    <section className="border-b border-border bg-card">
      <div className="mx-auto max-w-6xl px-6 py-20 md:py-28">
        <div className="space-y-3 max-w-2xl">
          <span className="text-sm font-medium uppercase tracking-wider text-primary">
            Design DNA
          </span>
          <h2 className="font-display text-3xl md:text-5xl font-bold tracking-tight text-foreground">
            Your visual identity, synthesized.
          </h2>
          <p className="text-lg text-muted-foreground leading-relaxed pt-2">
            Templates pick from a finite gallery. Pebble draws a fresh design DNA —
            fonts, palette, layout posture, signature moves — every time you generate.
            Run the questionnaire twice and get two different sites. That's not a bug,
            it's the point.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 pt-10">
          {DNA_VARIANTS.map((v, i) => (
            <motion.div
              key={v.id}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.5, delay: i * 0.08, ease: [0.22, 1, 0.36, 1] }}
              className="overflow-hidden rounded-2xl border border-border bg-background shadow-[var(--shadow-1)]"
            >
              <div
                className="h-32 flex items-center justify-center"
                style={{ background: v.swatches[1] }}
              >
                <span
                  className={`text-2xl font-bold ${v.font}`}
                  style={{ color: v.swatches[0] }}
                >
                  Wildflower Bakery
                </span>
              </div>
              <div className="border-t border-border p-5 space-y-3">
                <div className="flex items-center gap-2">
                  {v.swatches.map((c) => (
                    <span
                      key={c}
                      className="h-5 w-5 rounded-full border border-border"
                      style={{ backgroundColor: c }}
                    />
                  ))}
                </div>
                <p className="text-sm font-medium text-foreground">{v.label}</p>
                <p className="text-xs text-muted-foreground">
                  Same business, different DNA. Pebble picks signature moves to match.
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ---------------------------------------------------------- How It Works -- */

const STEPS = [
  {
    n: "01",
    title: "Tell us about your business",
    body: "10 questions, 3–4 minutes. What you do, who it's for, the tone you want. No design questions — Pebble figures those out.",
  },
  {
    n: "02",
    title: "Pebble builds your site",
    body: "Real industry research, generated images, a full design system, an end-to-end working site. About 10 minutes for a first build.",
  },
  {
    n: "03",
    title: "Tweak in plain English or click-to-edit",
    body: "Click any element to change text, color, or size. Or ask for refinements like \"make it friendlier\". Every edit is undoable.",
  },
];

function HowItWorks() {
  return (
    <section className="border-b border-border bg-background">
      <div className="mx-auto max-w-6xl px-6 py-20 md:py-28">
        <div className="text-center max-w-2xl mx-auto space-y-3">
          <span className="text-sm font-medium uppercase tracking-wider text-primary">
            How it works
          </span>
          <h2 className="font-display text-3xl md:text-5xl font-bold tracking-tight text-foreground">
            Three steps. No design background required.
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8 pt-12">
          {STEPS.map((s, i) => (
            <motion.div
              key={s.n}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.5, delay: i * 0.1, ease: [0.22, 1, 0.36, 1] }}
              className="rounded-2xl border border-border bg-card p-6 space-y-3"
            >
              <span className="font-display text-4xl font-bold text-primary">{s.n}</span>
              <h3 className="text-xl font-semibold text-foreground">{s.title}</h3>
              <p className="text-muted-foreground leading-relaxed">{s.body}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ----------------------------------------------------- What You Get cards -- */

const FEATURES = [
  {
    icon: MousePointerClick,
    title: "Click-to-edit visual editor",
    body: "Hover anything in the preview, click to select, change text/color/size from the side panel. Edits land in source files — they survive regeneration.",
  },
  {
    icon: History,
    title: "Version history with one-click undo",
    body: "Every refinement, every visual edit, every full regeneration snapshots first. Roll back to any prior version from a drawer.",
  },
  {
    icon: Wand2,
    title: "Migrate from your existing site",
    body: "Paste your current URL. Pebble extracts business facts, infers the industry, suggests a brief — then builds you something better.",
  },
  {
    icon: Shield,
    title: "Privacy-clean by default",
    body: "No Google Analytics, no Meta Pixel, no fingerprinting. A FOUNDATION eval check fails any build that ships a third-party tracker.",
  },
  {
    icon: ImageIcon,
    title: "Generated images, not stock photos",
    body: "Industry-aware Imagen calls produce on-brand visuals. No \"woman smiling at laptop\" template look.",
  },
  {
    icon: Sparkles,
    title: "Honest cost telemetry",
    body: "Every action shows whether it's free or billable. Visual edits and simple refinements never cost a credit. We tell you up front.",
  },
];

function FeatureGrid() {
  return (
    <section className="border-b border-border bg-card">
      <div className="mx-auto max-w-6xl px-6 py-20 md:py-28">
        <div className="text-center max-w-2xl mx-auto space-y-3">
          <span className="text-sm font-medium uppercase tracking-wider text-primary">
            What you get
          </span>
          <h2 className="font-display text-3xl md:text-5xl font-bold tracking-tight text-foreground">
            Built like a senior engineer would build it.
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-5 pt-12">
          {FEATURES.map((f, i) => {
            const Icon = f.icon;
            return (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.45, delay: (i % 3) * 0.05, ease: [0.22, 1, 0.36, 1] }}
                className="rounded-2xl border border-border bg-background p-6 space-y-3"
              >
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-accent">
                  <Icon className="h-5 w-5 text-primary" />
                </span>
                <h3 className="text-lg font-semibold text-foreground">{f.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{f.body}</p>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

/* ------------------------------------------------------------- Pricing -- */

const TIERS = [
  {
    name: "Free preview",
    price: "$0",
    period: "during preview",
    body: "Two sites. Full visual editor. Real undo. No card required.",
    cta: "Start free",
    href: "/workspace#phase=idea",
    featured: true,
    coming: false,
  },
  {
    name: "Pro",
    price: "$19",
    period: "/month",
    body: "Unlimited sites. LLM-backed refinements. Custom domain. Forms inbox.",
    cta: "Coming soon",
    href: "#",
    featured: false,
    coming: true,
  },
  {
    name: "Studio",
    price: "$49",
    period: "/month",
    body: "Everything in Pro plus multi-page generation, agency invoicing, and team seats.",
    cta: "Coming soon",
    href: "#",
    featured: false,
    coming: true,
  },
];

function Pricing() {
  return (
    <section className="border-b border-border bg-background">
      <div className="mx-auto max-w-6xl px-6 py-20 md:py-28">
        <div className="text-center max-w-2xl mx-auto space-y-3">
          <span className="text-sm font-medium uppercase tracking-wider text-primary">
            Pricing
          </span>
          <h2 className="font-display text-3xl md:text-5xl font-bold tracking-tight text-foreground">
            Try it for nothing. Pay later, if at all.
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 pt-12 max-w-4xl mx-auto">
          {TIERS.map((t) => (
            <div
              key={t.name}
              className={`rounded-2xl border p-6 space-y-4 ${
                t.featured
                  ? "border-primary bg-card shadow-[var(--shadow-1)]"
                  : "border-border bg-card opacity-90"
              }`}
            >
              <div>
                <h3 className="text-lg font-semibold text-foreground">{t.name}</h3>
                <div className="pt-2 flex items-baseline gap-1">
                  <span className="font-display text-4xl font-bold text-foreground">{t.price}</span>
                  <span className="text-sm text-muted-foreground">{t.period}</span>
                </div>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">{t.body}</p>
              {t.coming ? (
                <span className="inline-flex w-full items-center justify-center rounded-full border border-border bg-background px-4 py-2.5 text-sm font-medium text-muted-foreground">
                  {t.cta}
                </span>
              ) : (
                <Link
                  href={t.href}
                  className="inline-flex w-full items-center justify-center rounded-full bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground hover:scale-[1.02] transition-transform"
                >
                  {t.cta}
                </Link>
              )}
            </div>
          ))}
        </div>

        <p className="pt-8 text-center text-sm text-muted-foreground max-w-xl mx-auto">
          When billing ships, we'll be specific about what's billable and what's free. Visual
          edits and deterministic refinements will always be free — that's a promise, not a
          marketing line.
        </p>
      </div>
    </section>
  );
}

/* --------------------------------------------------------------- FAQ -- */

function FAQ() {
  const [open, setOpen] = useState<number | null>(0);
  return (
    <section className="border-b border-border bg-card">
      <div className="mx-auto max-w-3xl px-6 py-20 md:py-28">
        <div className="text-center space-y-3">
          <span className="text-sm font-medium uppercase tracking-wider text-primary">
            Questions
          </span>
          <h2 className="font-display text-3xl md:text-5xl font-bold tracking-tight text-foreground">
            Things people ask first.
          </h2>
        </div>

        <div className="pt-12 space-y-3">
          {FAQ_ITEMS.map((item, i) => {
            const isOpen = open === i;
            return (
              <div
                key={item.q}
                className="rounded-2xl border border-border bg-background overflow-hidden"
              >
                <button
                  onClick={() => setOpen(isOpen ? null : i)}
                  className="w-full text-left px-6 py-5 flex items-center justify-between gap-4 hover:bg-accent transition-colors"
                  aria-expanded={isOpen}
                >
                  <span className="font-medium text-foreground">{item.q}</span>
                  <ChevronDown
                    className={`h-5 w-5 text-muted-foreground transition-transform ${isOpen ? "rotate-180" : ""}`}
                  />
                </button>
                <motion.div
                  initial={false}
                  animate={{ height: isOpen ? "auto" : 0, opacity: isOpen ? 1 : 0 }}
                  transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
                  className="overflow-hidden"
                >
                  <p className="px-6 pb-5 text-muted-foreground leading-relaxed">
                    {item.a}
                  </p>
                </motion.div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

/* --------------------------------------------------- Final CTA + Footer -- */

function FinalCta() {
  return (
    <section className="border-b border-border bg-background">
      <div className="mx-auto max-w-4xl px-6 py-24 md:py-32 text-center space-y-8">
        <h2 className="font-display text-4xl md:text-6xl font-bold tracking-tight text-foreground">
          The first one's on us.
        </h2>
        <p className="text-lg md:text-xl text-muted-foreground max-w-xl mx-auto">
          Three minutes to answer ten questions. Ten more to see your site. Nothing to pay,
          nothing to install.
        </p>
        <Link
          href="/workspace#phase=idea"
          className="group inline-flex items-center gap-2 rounded-full bg-primary px-8 py-4 text-lg font-medium text-primary-foreground shadow-[var(--shadow-1)] transition-transform hover:scale-[1.02] active:scale-[0.98]"
        >
          Start building
          <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-0.5" />
        </Link>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="bg-background">
      <div className="mx-auto max-w-6xl px-6 py-10 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
        <span className="font-display text-xl font-bold tracking-tight text-foreground">
          Pebble.
        </span>
        <span>© {new Date().getFullYear()} Pebble Engine. Built with care.</span>
        <div className="flex items-center gap-5">
          <Link href="/migrate" className="hover:text-foreground transition-colors">Migrate</Link>
          <Link href="/workspace#phase=idea" className="hover:text-foreground transition-colors">Start</Link>
          <Link href="/" className="hover:text-foreground transition-colors">App</Link>
        </div>
      </div>
    </footer>
  );
}

/* ------------------------------------------------------------- Top bar -- */

function MarketingTopBar() {
  return (
    <header className="fixed top-0 inset-x-0 z-50 border-b border-border bg-background/85 backdrop-blur">
      <div className="mx-auto max-w-6xl px-6 h-16 flex items-center justify-between">
        <Link href="/landing" className="font-display text-2xl font-bold tracking-tight text-foreground">
          Pebble.
        </Link>
        <nav className="hidden md:flex items-center gap-7 text-sm text-muted-foreground">
          <a href="#dna" className="hover:text-foreground transition-colors">Design DNA</a>
          <a href="#how" className="hover:text-foreground transition-colors">How it works</a>
          <a href="#pricing" className="hover:text-foreground transition-colors">Pricing</a>
          <a href="#faq" className="hover:text-foreground transition-colors">FAQ</a>
        </nav>
        <div className="flex items-center gap-3">
          <AuthMenu />
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}

/* ----------------------------------------------------- Default export -- */

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      <MarketingTopBar />
      <div className="pt-16">
        <Hero />
        <section id="dna"><Differentiator /></section>
        <section id="how"><HowItWorks /></section>
        <FeatureGrid />
        <section id="pricing"><Pricing /></section>
        <section id="faq"><FAQ /></section>
        <FinalCta />
        <Footer />
      </div>
    </div>
  );
}
