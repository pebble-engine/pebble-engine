"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ChevronDown, LifeBuoy, Mail, Rocket, Globe, Lock, History, Sparkles } from "lucide-react";
import { TopNav } from "@/components/top-nav";
import { FAQ_BY_SECTION } from "@/lib/faq";

const TOPICS: { title: string; href: string; Icon: typeof LifeBuoy; lead: string }[] = [
  { title: "Publishing",         href: "#publishing",  Icon: Rocket,    lead: "Get your site live or download a ZIP." },
  { title: "Custom domains",     href: "#domains",     Icon: Globe,     lead: "Point yourbiz.com at your published site." },
  { title: "Passwords + login",  href: "#password",    Icon: Lock,      lead: "Reset, recover, and keep your account safe." },
  { title: "Edits + history",    href: "#history",     Icon: History,   lead: "Every change is undoable. Here's how." },
  { title: "Refinement chips",   href: "#refine",      Icon: Sparkles,  lead: "Which tweaks are free, which use credits." },
];

export default function HelpPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <TopNav projectName="Help" />

      <main className="flex-1 px-6 py-12 md:py-16">
        <div className="max-w-3xl mx-auto space-y-12">
          {/* Hero */}
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="text-center space-y-3"
          >
            <div className="w-14 h-14 rounded-full bg-primary/10 text-primary mx-auto flex items-center justify-center">
              <LifeBuoy className="w-7 h-7" />
            </div>
            <h1 className="font-display text-4xl md:text-5xl font-bold tracking-tight text-foreground">
              How can we help?
            </h1>
            <p className="text-muted-foreground">
              Everything Pebble does is editable, undoable, and explained. Start with a topic
              or scroll for the full FAQ.
            </p>
          </motion.div>

          {/* Topic grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {TOPICS.map((t) => (
              <a
                key={t.title}
                href={t.href}
                className="flex items-start gap-3 p-4 rounded-2xl border border-border bg-card hover:bg-accent transition-colors"
              >
                <div className="w-10 h-10 rounded-full bg-primary/10 text-primary flex items-center justify-center shrink-0">
                  <t.Icon className="w-5 h-5" />
                </div>
                <div>
                  <p className="font-display text-base font-semibold text-foreground">{t.title}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{t.lead}</p>
                </div>
              </a>
            ))}
          </div>

          {/* Detailed topic sections */}
          <TopicSection id="publishing" title="Publishing your site" Icon={Rocket}>
            <p>
              Open any project, then click <strong>Publish</strong> in the top right of the
              workspace. On the publish page click <strong>Publish now</strong>. Pebble
              snapshots your site (so the publish itself is undoable) and then either:
            </p>
            <ul className="list-disc pl-5 space-y-2">
              <li>
                <strong>Deploys to Cloudflare Pages</strong> if{" "}
                <code className="font-mono text-xs">CLOUDFLARE_ACCOUNT_ID</code> and{" "}
                <code className="font-mono text-xs">CLOUDFLARE_API_TOKEN</code> are in your{" "}
                <code className="font-mono text-xs">.env</code> file. You get a live URL like{" "}
                <code className="font-mono text-xs">pebble-yourname.pages.dev</code>.
              </li>
              <li>
                <strong>Builds a downloadable ZIP</strong> if those aren&apos;t set yet. Drag
                it into Vercel, Netlify, or any static host.
              </li>
            </ul>
            <p>
              The publish page shows a Cloudflare setup checklist when keys are missing —
              copy-paste-ready, ~5 minutes to wire up.
            </p>
          </TopicSection>

          <TopicSection id="domains" title="Connecting a custom domain" Icon={Globe}>
            <p>
              After publishing, expand the <strong>Connect a custom domain</strong> panel.
              Type the domain you own (like <code className="font-mono text-xs">yourbiz.com</code>),
              hit Connect, and Pebble shows the CNAME record to add at your DNS provider.
            </p>
            <p className="text-sm text-muted-foreground">
              The exact record looks like:{" "}
              <code className="font-mono text-xs">yourbiz.com CNAME pebble-yourbiz.pages.dev</code>
            </p>
            <p>
              Add it at GoDaddy / Namecheap / Cloudflare DNS / wherever your domain lives.
              DNS propagation usually takes a few minutes; the badge flips from
              &ldquo;DNS pending&rdquo; to <strong className="text-spark-deep">Live</strong> when
              it&apos;s ready.
            </p>
          </TopicSection>

          <TopicSection id="password" title="Passwords + recovery" Icon={Lock}>
            <p>
              If you forget your password, click <strong>Forgot your password?</strong> on
              the sign-in page. Type the email you used at signup; we email a one-time link
              that&apos;s good for an hour.
            </p>
            <p>
              When you finish a password reset, every other signed-in device gets signed
              out automatically — if your account ever got compromised, the reset evicts
              the attacker.
            </p>
          </TopicSection>

          <TopicSection id="history" title="Edits + undo" Icon={History}>
            <p>
              Every refinement, visual edit, and rollback creates a snapshot of your site.
              In the workspace, click the History icon (top right) to see them all.{" "}
              <strong>Restore</strong> any snapshot to roll back — the rollback itself is
              also snapshotted, so undoing the undo always works.
            </p>
            <p>
              Storage is intentionally simple: each snapshot is a full copy of the site
              folder under <code className="font-mono text-xs">output/&lt;slug&gt;/history/</code>.
              We can switch to packed/diffed storage later if disk pressure shows up.
            </p>
          </TopicSection>

          <TopicSection id="refine" title="Which tweaks use credits" Icon={Sparkles}>
            <p>
              The refinement chip bar at the bottom of the workspace has a colored dot on
              each chip:
            </p>
            <ul className="list-disc pl-5 space-y-2">
              <li>
                <span className="inline-block w-2.5 h-2.5 rounded-full bg-earth mr-1.5 align-middle" />
                <strong className="text-earth-deep">Earth (free):</strong>{" "}
                <em>Simpler</em>, <em>Change colors</em>. These are deterministic — Pebble
                rotates the brand-safe palette or tones down decorative effects with regex.
                No LLM call.
              </li>
              <li>
                <span className="inline-block w-2.5 h-2.5 rounded-full bg-spark mr-1.5 align-middle" />
                <strong className="text-spark-deep">Spark (uses credits):</strong>{" "}
                <em>Friendlier</em>, <em>Professional</em>, <em>Add booking</em>. These
                rewrite copy or add new sections via the LLM — that&apos;s what costs.
              </li>
            </ul>
            <p>
              Visual edits — clicking an element to change its text, color, or font size —
              are always free. They never call the LLM.
            </p>
          </TopicSection>

          {/* Full FAQ */}
          {FAQ_BY_SECTION.map((section) => (
            <section key={section.title} className="space-y-3">
              <h2 className="font-display text-2xl font-bold tracking-tight text-foreground">
                {section.title}
              </h2>
              <FaqAccordion items={section.items} />
            </section>
          ))}

          {/* Contact */}
          <section className="border-t border-border pt-10 text-center space-y-3">
            <Mail className="w-6 h-6 mx-auto text-muted-foreground" />
            <h2 className="font-display text-xl font-semibold text-foreground">
              Still stuck?
            </h2>
            <p className="text-sm text-muted-foreground">
              Email <a href="mailto:hello@pebbleapp.ai" className="text-primary hover:underline">hello@pebbleapp.ai</a>{" "}
              and we&apos;ll get back to you.
            </p>
            <p className="text-xs text-muted-foreground">
              <Link href="/landing" className="hover:text-foreground">Back to the landing page</Link>
              {"  ·  "}
              <Link href="/" className="hover:text-foreground">Start a new site</Link>
            </p>
          </section>
        </div>
      </main>
    </div>
  );
}

// ---------------------------------------------------------------------------

function TopicSection({
  id, title, Icon, children,
}: { id: string; title: string; Icon: typeof LifeBuoy; children: React.ReactNode }) {
  return (
    <section id={id} className="space-y-3 scroll-mt-24">
      <div className="flex items-center gap-2 pt-2">
        <Icon className="w-5 h-5 text-primary" />
        <h2 className="font-display text-2xl font-bold tracking-tight text-foreground">{title}</h2>
      </div>
      <div className="prose prose-sm dark:prose-invert max-w-none space-y-3 text-foreground leading-relaxed">
        {children}
      </div>
    </section>
  );
}

function FaqAccordion({ items }: { items: { q: string; a: string }[] }) {
  const [open, setOpen] = useState<number | null>(0);
  return (
    <div className="space-y-2">
      {items.map((item, i) => {
        const isOpen = open === i;
        return (
          <div key={item.q} className="rounded-xl border border-border bg-card overflow-hidden">
            <button
              onClick={() => setOpen(isOpen ? null : i)}
              className="w-full text-left px-5 py-4 flex items-center justify-between gap-4 hover:bg-accent transition-colors"
              aria-expanded={isOpen}
            >
              <span className="font-medium text-foreground">{item.q}</span>
              <ChevronDown
                className={`w-5 h-5 text-muted-foreground transition-transform shrink-0 ${isOpen ? "rotate-180" : ""}`}
              />
            </button>
            <motion.div
              initial={false}
              animate={{ height: isOpen ? "auto" : 0, opacity: isOpen ? 1 : 0 }}
              transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
              className="overflow-hidden"
            >
              <p className="px-5 pb-4 text-muted-foreground leading-relaxed">{item.a}</p>
            </motion.div>
          </div>
        );
      })}
    </div>
  );
}
