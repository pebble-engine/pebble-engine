"use client";

/**
 * Peblet Docs — search-driven help panel (2026-05-23).
 *
 * Marc's brief: don't let users feel lost. The Docs tab is a
 * searchable index of help topics + a "Ask Peblet" handoff for
 * anything not covered by the static index. Clicking a topic
 * either deep-links to the relevant page or hands the query to
 * the chat tab so Peblet answers in conversation.
 *
 * Tiny static index (~30 entries) is the right shape today. When
 * we have a real help CMS or vector search, swap the source for
 * a remote search endpoint — the UI doesn't change.
 */

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Search, MessageSquare, ExternalLink } from "lucide-react";

type DocEntry = {
  title:    string;
  blurb:    string;
  /** Path the topic lives on, or `chat:` to hand off to the chat tab. */
  href:     string;
  /** Free-text tags for fuzzy search beyond title match. */
  keywords: string[];
};

const INDEX: DocEntry[] = [
  // Building
  { title: "Build a new site",       blurb: "Start the questionnaire flow",          href: "/workspace#phase=welcome",     keywords: ["new", "create", "build", "start"] },
  { title: "Browse templates",       blurb: "Pre-made starting points",              href: "/templates",                    keywords: ["template", "starter", "gallery"] },
  { title: "Edit a published site",  blurb: "Click-to-edit, refine, undo",           href: "chat:How do I edit my published site?", keywords: ["edit", "change", "update", "modify"] },
  { title: "Add a section",          blurb: "Drop in testimonials, FAQ, etc.",       href: "chat:How do I add a section?",  keywords: ["section", "block", "testimonials", "faq"] },
  { title: "Undo a change",          blurb: "Every refinement is reversible",        href: "chat:How do I undo a change?",  keywords: ["undo", "revert", "history", "rollback"] },

  // Publishing
  { title: "Custom domain",          blurb: "Connect yourdomain.com in one DNS record", href: "chat:How do I connect a custom domain?", keywords: ["domain", "dns", "cname", "publish"] },
  { title: "Publish for free",       blurb: "Get a free pebbleapp.ai subdomain",     href: "chat:How do I publish for free?", keywords: ["publish", "deploy", "live", "free"] },
  { title: "Site analytics",         blurb: "Plausible page-view dashboard",         href: "/integrations",                 keywords: ["analytics", "visits", "traffic", "plausible"] },

  // Billing
  { title: "Pricing plans",          blurb: "What's in each tier",                   href: "/pricing",                      keywords: ["pricing", "plan", "cost", "tier", "starter", "pro"] },
  { title: "Open billing portal",    blurb: "Manage card + invoices",                href: "chat:Open my billing portal",   keywords: ["billing", "card", "invoice", "payment", "stripe"] },
  { title: "Cancel subscription",    blurb: "How cancellation works",                href: "chat:How do I cancel my subscription?", keywords: ["cancel", "downgrade", "subscription"] },
  { title: "Refunds",                blurb: "No-questions-asked inside 7 days",      href: "chat:What's your refund policy?", keywords: ["refund", "money back"] },

  // Integrations
  { title: "Stripe payments",        blurb: "Take card payments on your site",       href: "/integrations",                 keywords: ["stripe", "payment", "checkout"] },
  { title: "Resend (email)",         blurb: "Form auto-responders, drips",           href: "/integrations",                 keywords: ["resend", "email", "smtp"] },
  { title: "Calendly bookings",      blurb: "Embed scheduler in your site",          href: "/integrations",                 keywords: ["calendly", "booking", "schedule"] },
  { title: "Webhook for form data",  blurb: "POST submissions to any URL",           href: "/integrations",                 keywords: ["webhook", "zapier", "form"] },

  // Community
  { title: "Launchpad showcase",     blurb: "Get featured in the gallery",           href: "/community/launchpad",          keywords: ["showcase", "featured", "launchpad", "gallery"] },
  { title: "Affiliate program",      blurb: "Earn for every referral",               href: "/community/affiliate",          keywords: ["affiliate", "referral", "commission"] },
  { title: "Hire a partner",         blurb: "Designers + agencies for hire",         href: "/community/hire-a-partner",     keywords: ["partner", "hire", "agency", "freelance"] },

  // Account
  { title: "Account settings",       blurb: "Profile, password, danger zone",        href: "/settings",                     keywords: ["account", "profile", "settings", "password"] },
  { title: "Delete account",         blurb: "Permanent, 7-day cooling-off",          href: "chat:How do I delete my account?", keywords: ["delete", "remove", "gdpr"] },

  // Trust
  { title: "Privacy & Trust Charter", blurb: "How Pebble handles your data",         href: "/trust",                        keywords: ["privacy", "trust", "data", "gdpr", "charter"] },
];

function scoreEntry(entry: DocEntry, q: string): number {
  if (!q) return 0;
  const needle = q.toLowerCase();
  const haystack = `${entry.title} ${entry.blurb} ${entry.keywords.join(" ")}`.toLowerCase();
  if (entry.title.toLowerCase().startsWith(needle)) return 100;
  if (entry.title.toLowerCase().includes(needle)) return 60;
  if (haystack.includes(needle)) return 20;
  return 0;
}

export function PebletDocs({
  onAskInChat,
}: {
  /** Called when the user picks an entry whose href is "chat:..." —
   *  hands the query off to the Chat tab so Peblet answers conversationally. */
  onAskInChat: (question: string) => void;
}) {
  const router = useRouter();
  const [query, setQuery] = useState("");

  const results = useMemo(() => {
    const q = query.trim();
    if (!q) return INDEX;
    return INDEX
      .map((e) => ({ e, s: scoreEntry(e, q) }))
      .filter((x) => x.s > 0)
      .sort((a, b) => b.s - a.s)
      .map((x) => x.e);
  }, [query]);

  const handlePick = (entry: DocEntry) => {
    if (entry.href.startsWith("chat:")) {
      onAskInChat(entry.href.slice(5));
      return;
    }
    router.push(entry.href);
  };

  const trimmedQuery = query.trim();
  const noResults = trimmedQuery && results.length === 0;

  return (
    <div className="flex-1 flex flex-col min-h-0">
      <div className="px-4 py-3 border-b border-border shrink-0">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search Pebble docs..."
            className="w-full bg-background border border-border rounded-lg pl-9 pr-3 py-2 text-sm text-foreground placeholder-muted-foreground/70 focus:outline-none focus:border-primary/60 focus:ring-2 focus:ring-primary/20"
            autoFocus
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-2 py-2">
        {noResults && (
          <div className="px-4 py-8 text-center space-y-3">
            <p className="text-sm text-muted-foreground">
              Nothing matched &ldquo;{trimmedQuery}&rdquo; in the index.
            </p>
            <button
              type="button"
              onClick={() => onAskInChat(trimmedQuery)}
              className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-foreground text-background text-xs font-semibold hover:opacity-90"
            >
              <MessageSquare className="w-3.5 h-3.5" />
              Ask Peblet instead
            </button>
          </div>
        )}

        {!noResults && (
          <ul className="space-y-0.5">
            {results.map((entry) => {
              const handsToChat = entry.href.startsWith("chat:");
              return (
                <li key={entry.title}>
                  <button
                    type="button"
                    onClick={() => handlePick(entry)}
                    className="w-full text-left flex items-start justify-between gap-3 px-3 py-2.5 rounded-lg hover:bg-accent transition-colors group"
                  >
                    <span className="flex flex-col gap-0.5 min-w-0">
                      <span className="text-sm font-semibold text-foreground leading-tight">
                        {entry.title}
                      </span>
                      <span className="text-xs text-muted-foreground leading-snug">
                        {entry.blurb}
                      </span>
                    </span>
                    <span className="shrink-0 text-muted-foreground group-hover:text-foreground mt-0.5">
                      {handsToChat ? (
                        <MessageSquare className="w-3.5 h-3.5" />
                      ) : (
                        <ExternalLink className="w-3.5 h-3.5" />
                      )}
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}
