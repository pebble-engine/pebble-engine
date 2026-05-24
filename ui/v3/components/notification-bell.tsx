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
import {
  fetchNotifications,
  markNotificationRead,
  markAllNotificationsRead,
  type NotificationItem,
} from "@/lib/api";

type NotificationKind = "welcome" | "community" | "template" | "tip" | "billing" | "system" | string;

type Notification = {
  id:    string;
  kind:  NotificationKind;
  title: string;
  body:  string;
  /** Internal route to navigate to on click, OR an external URL. */
  href?: string;
  /** ISO timestamp — used to sort newest-first. */
  at:    string;
  /** True when the row came from Supabase (so we use the server's
   *  read-state instead of localStorage). */
  remote?: boolean;
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

// Map an event kind from the server to the NotificationKind we use
// for icon coloring. Unknowns fall back to "system" so the bell never
// breaks on a new kind we haven't styled yet.
function mapKind(kind: string): NotificationKind {
  if (kind === "build_completed" || kind === "site_published") return "system";
  if (kind === "joined_pebble") return "welcome";
  if (kind === "template_used" || kind === "template_submitted") return "template";
  if (kind === "tip") return "tip";
  if (kind === "welcome") return "welcome";
  return "system";
}

// Build a deep link from a server event's `meta` payload. Falls back
// to /dashboard when we can't deduce one.
function hrefFor(item: NotificationItem): string {
  const meta = item.meta || {};
  if (typeof meta.slug === "string" && meta.slug) {
    return `/workspace/${encodeURIComponent(meta.slug)}`;
  }
  if (typeof meta.url === "string" && meta.url.startsWith("http")) {
    return meta.url;
  }
  return "/dashboard";
}

export function NotificationBell() {
  const [open, setOpen] = useState(false);
  // localStorage read-state for the SEED rows (no server-side row to
  // mark). Server events get their read-state from Supabase via the
  // is_read field returned by /api/notifications.
  const [seedReadIds, setSeedReadIds] = useState<Set<string>>(() => new Set());
  // Server-side notifications. Empty array means either no events yet
  // OR the fetch failed; the bell merges these with SEED so the user
  // always sees SOMETHING the first time they log in.
  const [serverItems, setServerItems] = useState<NotificationItem[]>([]);
  const [serverUnread, setServerUnread] = useState<number>(0);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Hydrate localStorage seed-read state + fetch server items on mount.
  useEffect(() => {
    setSeedReadIds(loadReadIds());
    void refresh();
  }, []);

  async function refresh() {
    try {
      const res = await fetchNotifications();
      setServerItems(res.notifications || []);
      setServerUnread(res.unread_count || 0);
    } catch {
      // 401 (signed out) or 500 — silently leave server list empty.
      // Seed notifications still render so the bell is never blank.
      setServerItems([]);
      setServerUnread(0);
    }
  }

  // Re-fetch when the dropdown opens so the bell stays fresh without
  // a noisy polling loop. Cheap (one tiny GET).
  useEffect(() => {
    if (open) void refresh();
  }, [open]);

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

  // Combine server rows + local SEED. Server rows surface first
  // because they're the real signal; SEED nudges go below.
  const merged: Array<Notification & { isUnread: boolean }> = [
    ...serverItems.map((s) => ({
      id:       s.id,
      kind:     mapKind(s.kind),
      title:    s.title,
      body:     s.body || "",
      href:     hrefFor(s),
      at:       s.created_at,
      remote:   true,
      isUnread: !s.is_read,
    })),
    ...SEED.map((n) => ({
      ...n,
      remote:   false,
      isUnread: !seedReadIds.has(n.id),
    })),
  ];
  const unreadCount = serverUnread + SEED.filter((n) => !seedReadIds.has(n.id)).length;

  const markRead = async (item: { id: string; remote?: boolean }) => {
    if (item.remote) {
      // Optimistically flip the row + decrement the badge before the
      // network round-trip; the API call is fire-and-forget on success
      // because we already updated state.
      setServerItems((prev) => prev.map((s) => s.id === item.id ? { ...s, is_read: true } : s));
      setServerUnread((c) => Math.max(0, c - 1));
      try {
        await markNotificationRead(item.id);
      } catch {
        // If the network call failed, the local state still shows
        // read — Marc gets to click again, which will retry. Not
        // worth a rollback dance for a notification.
      }
    } else {
      const next = new Set(seedReadIds);
      next.add(item.id);
      setSeedReadIds(next);
      persistReadIds(next);
    }
  };

  const markAllRead = async () => {
    // Local seed first (instant).
    const seedAll = new Set(SEED.map((n) => n.id));
    setSeedReadIds(seedAll);
    persistReadIds(seedAll);
    // Then server.
    setServerItems((prev) => prev.map((s) => ({ ...s, is_read: true })));
    setServerUnread(0);
    try {
      await markAllNotificationsRead();
    } catch {
      // Best-effort; same reasoning as markRead above.
    }
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
            {merged.map((n) => {
              const Icon = ICON_FOR[n.kind] ?? Bell;
              const isUnread = n.isUnread;
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
                    {n.body && <p className="text-xs text-muted-foreground mt-1 leading-snug">{n.body}</p>}
                  </div>
                </div>
              );
              return (
                <li key={`${n.remote ? "r" : "s"}-${n.id}`}>
                  {n.href ? (
                    <Link
                      href={n.href}
                      onClick={() => { void markRead(n); setOpen(false); }}
                    >
                      {content}
                    </Link>
                  ) : (
                    <button
                      type="button"
                      onClick={() => void markRead(n)}
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
