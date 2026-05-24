"use client";

/**
 * NotificationBell — TopNav bell with badge + dropdown (2026-05-23).
 *
 * Marc's brief: "force as much community engagement as possible."
 * The bell is the always-visible nudge surface. Each notification is
 * a clickable row that either deep-links (community post, template,
 * settings) or kicks off an action.
 *
 * Source today: a curated seed list + per-user read state stored in
 * localStorage. No backend events yet. Designed so swapping in a
 * remote /api/notifications endpoint is a single fetch swap with the
 * Notification type unchanged.
 *
 * Why client-side state for now: a real notification backend needs a
 * Supabase table + RLS + push triggers from every event source (build
 * complete, new template, community post, billing alert). That's
 * its own project. The seed list ships the visible affordance + the
 * dropdown UX + the badge count today, so the bell isn't a fake
 * mock — it's a real surface with curated content.
 */

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Bell, Sparkles, Users, Rocket, CreditCard, BookOpen, type LucideIcon } from "lucide-react";

type NotificationKind = "welcome" | "community" | "template" | "tip" | "billing" | "system";

type Notification = {
  id:    string;
  kind:  NotificationKind;
  title: string;
  body:  string;
  /** Internal route to navigate to on click, OR an external URL. */
  href?: string;
  /** ISO timestamp — used to sort newest-first. */
  at:    string;
};

// Seed list. Marc 2026-05-23: pre-populate with welcome + community-
// nudge + tip notifications so the bell feels alive on day one. When
// the real event source ships, this becomes the fallback for new
// users / empty inboxes.
const SEED: Notification[] = [
  {
    id:    "welcome-1",
    kind:  "welcome",
    title: "Welcome to Pebble",
    body:  "Peblet is here to help — open the chat panel anytime. Hit Cmd-K to start a conversation from any page.",
    href:  "/dashboard",
    at:    "2026-05-23T22:00:00Z",
  },
  {
    id:    "community-launchpad",
    kind:  "community",
    title: "See what others built",
    body:  "Real sites from the Pebble community. Get featured by submitting yours.",
    href:  "/community/launchpad",
    at:    "2026-05-23T21:00:00Z",
  },
  {
    id:    "community-affiliate",
    kind:  "community",
    title: "Earn from referrals",
    body:  "Pebble's affiliate program pays for every friend you bring in. One link, lifetime commission.",
    href:  "/community/affiliate",
    at:    "2026-05-23T20:00:00Z",
  },
  {
    id:    "tip-domain",
    kind:  "tip",
    title: "Custom domain takes one DNS record",
    body:  "Your site can live at yourdomain.com — Setup walks you through it.",
    href:  "/integrations",
    at:    "2026-05-23T19:00:00Z",
  },
  {
    id:    "template-explore",
    kind:  "template",
    title: "Browse 20+ free templates",
    body:  "Industry-tuned starting points. One click clones to your project.",
    href:  "/templates",
    at:    "2026-05-23T18:00:00Z",
  },
];

const STORAGE_KEY = "pebble.notifications.read.v1";

function loadReadIds(): Set<string> {
  if (typeof window === "undefined") return new Set();
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return new Set();
    const parsed = JSON.parse(raw);
    return new Set(Array.isArray(parsed) ? parsed.map(String) : []);
  } catch {
    return new Set();
  }
}

function persistReadIds(ids: Set<string>): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify([...ids]));
  } catch {
    // localStorage can throw in incognito / quota-exceeded — silently ignore.
  }
}

const ICON_FOR: Record<NotificationKind, LucideIcon> = {
  welcome:   Sparkles,
  community: Users,
  template:  Rocket,
  tip:       BookOpen,
  billing:   CreditCard,
  system:    Bell,
};

export function NotificationBell() {
  const [open, setOpen] = useState(false);
  const [readIds, setReadIds] = useState<Set<string>>(() => new Set());
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Hydrate read-state from localStorage on mount. Done in useEffect
  // not useState init so the SSR + first-client renders match (no
  // hydration mismatch flicker).
  useEffect(() => {
    setReadIds(loadReadIds());
  }, []);

  // Click-outside closes the dropdown.
  useEffect(() => {
    if (!open) return;
    function onDocClick(e: MouseEvent) {
      if (!containerRef.current?.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, [open]);

  // Esc closes the dropdown too.
  useEffect(() => {
    if (!open) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open]);

  const unread = SEED.filter((n) => !readIds.has(n.id));
  const unreadCount = unread.length;

  const markRead = (id: string) => {
    const next = new Set(readIds);
    next.add(id);
    setReadIds(next);
    persistReadIds(next);
  };

  const markAllRead = () => {
    const next = new Set(SEED.map((n) => n.id));
    setReadIds(next);
    persistReadIds(next);
  };

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="relative p-2 rounded-full text-foreground hover:bg-accent transition-colors"
        aria-label={unreadCount > 0 ? `Notifications, ${unreadCount} unread` : "Notifications"}
        aria-haspopup="menu"
        aria-expanded={open}
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 inline-flex items-center justify-center min-w-[18px] h-[18px] px-1 text-[10px] font-bold text-primary-foreground bg-primary rounded-full">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div
          role="menu"
          className="absolute right-0 mt-2 w-[360px] z-50 rounded-2xl border border-border bg-card shadow-[0_12px_40px_rgba(0,0,0,0.18)] overflow-hidden"
        >
          <div className="flex items-center justify-between px-4 py-3 border-b border-border">
            <div>
              <p className="text-sm font-bold text-foreground">Notifications</p>
              <p className="text-[11px] text-muted-foreground">
                {unreadCount === 0 ? "All caught up" : `${unreadCount} unread`}
              </p>
            </div>
            {unreadCount > 0 && (
              <button
                type="button"
                onClick={markAllRead}
                className="text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors"
              >
                Mark all read
              </button>
            )}
          </div>

          <ul className="max-h-[420px] overflow-y-auto">
            {SEED.map((n) => {
              const Icon = ICON_FOR[n.kind];
              const isUnread = !readIds.has(n.id);
              const content = (
                <div className="flex items-start gap-3 px-4 py-3 hover:bg-accent transition-colors cursor-pointer">
                  <span
                    className={`mt-0.5 w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                      isUnread ? "bg-primary/15 text-primary" : "bg-muted text-muted-foreground"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className={`text-sm leading-tight ${isUnread ? "font-bold text-foreground" : "font-semibold text-muted-foreground"}`}>
                        {n.title}
                      </p>
                      {isUnread && <span className="inline-block w-1.5 h-1.5 rounded-full bg-primary shrink-0" />}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1 leading-snug">{n.body}</p>
                  </div>
                </div>
              );
              return (
                <li key={n.id}>
                  {n.href ? (
                    <Link
                      href={n.href}
                      onClick={() => { markRead(n.id); setOpen(false); }}
                    >
                      {content}
                    </Link>
                  ) : (
                    <button
                      type="button"
                      onClick={() => markRead(n.id)}
                      className="w-full text-left"
                    >
                      {content}
                    </button>
                  )}
                </li>
              );
            })}
          </ul>

          <div className="px-4 py-2.5 border-t border-border bg-muted/30 text-center">
            <Link
              href="/community"
              onClick={() => setOpen(false)}
              className="text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors"
            >
              Visit the community →
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
