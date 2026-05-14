"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Edit3, Sparkles } from "lucide-react";
import { TopNav } from "@/components/top-nav";
import { getBrief, getPlan, setLastBuild, type PebblePlan } from "@/lib/state";
import { generateSite } from "@/lib/api";

const cardVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0 },
};

function Card({ children, delay = 0, className = "" }: { children: React.ReactNode; delay?: number; className?: string }) {
  return (
    <motion.article
      variants={cardVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.45, delay, ease: [0.4, 0, 0.2, 1] }}
      className={`bg-card border border-border rounded-2xl p-8 shadow-[var(--shadow-1)] ${className}`}
    >
      {children}
    </motion.article>
  );
}

export default function PlanReviewPage() {
  const router = useRouter();
  const [plan, setPlan] = useState<PebblePlan | null>(null);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const p = getPlan();
    if (!p) {
      router.push("/");
      return;
    }
    setPlan(p);
  }, [router]);

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);
    try {
      const result = await generateSite(getBrief());
      setLastBuild(result);
      router.push("/workspace");
    } catch (e) {
      const msg = e instanceof Error ? e.message : "unknown error";
      setError(msg);
      setGenerating(false);
    }
  };

  if (!plan) {
    return (
      <div className="min-h-screen flex flex-col">
        <TopNav />
        <main className="flex-1 flex items-center justify-center text-muted-foreground">Loading plan…</main>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <TopNav />
      <main className="flex-1 px-4 py-12 max-w-3xl mx-auto w-full space-y-8">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="text-center space-y-2"
        >
          <h1 className="font-display text-4xl md:text-5xl font-bold text-primary">The Pebble Plan</h1>
          <p className="text-muted-foreground">Verify what I&apos;ll build before I generate the first draft. Edit anything below.</p>
        </motion.div>

        <Card delay={0.05}>
          <div className="flex justify-between items-start mb-4">
            <h3 className="font-display text-2xl font-semibold text-primary">Who I think this is for</h3>
            <span className="px-2 py-0.5 rounded text-xs font-mono uppercase tracking-wider text-muted-foreground bg-accent">
              Audience
            </span>
          </div>
          <p className="leading-relaxed text-foreground">{plan.audience}</p>
          <div className="flex gap-3 mt-6">
            <button className="bg-primary text-primary-foreground px-5 py-2 rounded font-semibold text-sm hover:opacity-90 transition-opacity">
              Looks right
            </button>
            <button className="border border-border bg-card text-foreground px-5 py-2 rounded font-semibold text-sm hover:bg-accent transition-colors flex items-center gap-1.5">
              <Edit3 className="w-3.5 h-3.5" /> Let me edit
            </button>
          </div>
        </Card>

        <Card delay={0.1}>
          <h3 className="font-display text-2xl font-semibold text-primary mb-4">The one thing I&apos;m optimizing for</h3>
          <p className="leading-relaxed text-foreground">{plan.goal}</p>
        </Card>

        <Card delay={0.15}>
          <h3 className="font-display text-2xl font-semibold text-primary mb-6">Pages I&apos;ll create</h3>
          <div className="space-y-3">
            {plan.pages.map((page, i) => (
              <motion.div
                key={page.id}
                initial={{ opacity: 0, x: -8 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.05 * i, duration: 0.3 }}
                className="flex justify-between items-start py-3 border-b border-border last:border-0"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-foreground">{page.title}</span>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                        page.foundation
                          ? "bg-secondary/20 text-secondary"
                          : "bg-spark/15 text-spark"
                      }`}
                    >
                      {page.foundation ? "Foundation" : "Industry"}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground mt-0.5">{page.purpose}</p>
                </div>
                <span className="text-xs font-mono text-muted-foreground/60">{page.route}</span>
              </motion.div>
            ))}
          </div>
        </Card>

        <Card delay={0.2}>
          <h3 className="font-display text-2xl font-semibold text-primary mb-4">Core capabilities</h3>
          <div className="flex flex-wrap gap-2">
            {plan.features.map((f, i) => (
              <motion.span
                key={f.id}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 0.04 * i, duration: 0.25 }}
                className="px-4 py-2 bg-background border border-border rounded-full text-sm font-medium"
              >
                {f.label}
              </motion.span>
            ))}
          </div>
        </Card>

        <Card delay={0.25} className="overflow-hidden p-0">
          <div className="p-8 border-b border-border">
            <h3 className="font-display text-2xl font-semibold text-primary">Visual style</h3>
            <p className="text-sm text-muted-foreground italic mt-1">Inspired by {plan.style.label}</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2">
            <div className="p-8 bg-background">
              <p className="font-display text-3xl text-foreground leading-tight">{plan.style.mood || plan.style.label}</p>
              <p className="font-mono text-xs text-muted-foreground mt-2">DNA-driven layout</p>
            </div>
            <div className="p-8 border-t md:border-t-0 md:border-l border-border space-y-6">
              <div>
                <p className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-2">Palette</p>
                <div className="flex gap-2">
                  {Object.entries(plan.style.palette || {}).map(([name, hex]) =>
                    hex ? (
                      <motion.div
                        key={name}
                        whileHover={{ scale: 1.15, y: -2 }}
                        className="w-12 h-12 rounded-full border border-border shadow-sm"
                        style={{ backgroundColor: hex }}
                        title={`${name}: ${hex}`}
                      />
                    ) : null,
                  )}
                </div>
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-2">Typography</p>
                <p className="font-display text-xl text-primary">{plan.style.fonts.display || "—"}</p>
                <p className="text-base text-foreground">{plan.style.fonts.body || "—"}</p>
              </div>
            </div>
          </div>
        </Card>

        <Card delay={0.3}>
          <h3 className="font-display text-2xl font-semibold text-primary mb-2">Launch setup</h3>
          <p className="text-sm text-muted-foreground mb-4">
            {plan.setup_needs.length} items. Pebble handles what it can; the rest is honest about what&apos;s coming or what you&apos;ll do.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {plan.setup_needs.map((item, i) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 4 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.03 * i, duration: 0.25 }}
                className="flex justify-between items-center p-3 bg-background rounded-lg border border-border"
                title={item.notes}
              >
                <span className="text-sm font-medium">{item.label}</span>
                <span
                  className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${
                    item.status === "auto"
                      ? "bg-earth/20 text-earth"
                      : item.status === "pending"
                        ? "bg-spark/15 text-spark"
                        : "bg-muted text-muted-foreground"
                  }`}
                >
                  {item.status === "auto" ? "Auto" : item.status === "pending" ? "Soon" : "You"}
                </span>
              </motion.div>
            ))}
          </div>
        </Card>

        <div className="pt-6 flex flex-col items-center gap-4">
          <motion.button
            whileTap={{ scale: 0.97 }}
            onClick={handleGenerate}
            disabled={generating}
            className="w-full md:w-auto min-w-[320px] bg-primary text-primary-foreground font-semibold py-4 px-8 rounded-full shadow-lg hover:translate-y-[-2px] active:translate-y-0 transition-all disabled:opacity-60 flex items-center justify-center gap-2"
          >
            {generating ? (
              <>
                <Sparkles className="w-4 h-4 animate-pulse" /> Generating…
              </>
            ) : (
              "Generate my draft"
            )}
          </motion.button>
          <button className="text-primary text-sm font-semibold hover:opacity-80 transition-opacity">
            Save the plan, generate later
          </button>
        </div>

        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-4 bg-destructive/10 border border-destructive/40 rounded-lg text-destructive text-sm"
            >
              {error}
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
