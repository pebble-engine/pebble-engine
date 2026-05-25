"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Home,
  Star,
  Clock,
  Search as SearchIcon,
  Plus,
  ExternalLink,
  Trash2,
  Globe,
  Download,
  Mail,
  Search,
  Sparkles,
  Compass,
  Users,
  ArrowRight,
  Undo2,
} from "lucide-react";
import { TopNav } from "@/components/top-nav";
import { ControlCenter } from "@/components/control-center";
import { DashboardSidebar } from "@/components/workspace/dashboard-sidebar";
import { PebletMascot } from "@/components/peblet-mascot";
import { MetallicPebbleLogo } from "@/components/metallic-pebble-logo";
import { NotificationBell } from "@/components/notification-bell";
import { useAuth } from "@/components/auth-provider";
import { getUserProfile } from "@/lib/state";
import { buildGreeting } from "@/lib/greeting";
import { type } from "@/lib/type";
import {
  listProjects,
  toggleStar,
  fetchActivity,
  deleteProject,
  rollback,
  type ProjectSummary,
  type ActivityRow,
  type ChatProjectContext,
} from "@/lib/api";
import { interactions } from "@/lib/interactions";

type Filter = "all" | "starred" | "recents";

export default function DashboardPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [activity, setActivity] = useState<ActivityRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<Filter>("all");
  const [query, setQuery] = useState("");
  const [deleting, setDeleting] = useState<string | null>(null); // slug pending confirm

  // Gmail-style undo: when the user clicks Delete on the inline overlay,
  // optimistically yank the row, show a toast for 5s, and only fire the
  // actual DELETE request when the timer expires. Click Undo within the
  // window → cancel the timer, put the row back, no API call. Only one
  // pending delete at a time — starting a second flushes the first.
  type PendingDelete = {
    slug: string;
    business_name: string;
    project: ProjectSummary;
    timeoutId: ReturnType<typeof setTimeout>;
    startedAt: number;
  };
  const [pendingDelete, setPendingDelete] = useState<PendingDelete | null>(null);
  // Ref mirrors the state so unmount + "flush previous" can clear timers
  // without stale-closure surprises.
  const pendingDeleteRef = useRef<PendingDelete | null>(null);
  useEffect(() => { pendingDeleteRef.current = pendingDelete; }, [pendingDelete]);

  // Restore-from-activity toast — fires after a successful inline
  // rollback from the ActivityFeed. Auto-dismisses after 5s. The
  // `tone` lets us reuse the same toast surface for the failure path.
  type RestoreToast = {
    tone: "success" | "error";
    message: string;
    slug?: string;       // success only — drives the "Open workspace" link
    timestamp: number;   // disambiguates rapid-fire toasts in AnimatePresence
  };
  const [restoreToast, setRestoreToast] = useState<RestoreToast | null>(null);
  useEffect(() => {
    if (!restoreToast) return;
    const id = setTimeout(() => setRestoreToast(null), 5000);
    return () => clearTimeout(id);
  }, [restoreToast]);

  /** Confirm + fire a rollback for an ActivityFeed row. */
  async function handleRestoreFromActivity(row: ActivityRow) {
    const niceWhen = formatRelative(row.written_at);
    const ok = window.confirm(
      `Restore ${row.business_name} to this snapshot (${niceWhen})? Current state is auto-snapshotted first so this is reversible.`,
    );
    if (!ok) return;
    try {
      await rollback(row.slug, row.snapshot_id);
      setRestoreToast({
        tone: "success",
        message: `Restored ${row.business_name} to ${niceWhen}.`,
        slug: row.slug,
        timestamp: Date.now(),
      });
      void refresh();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Couldn't restore that snapshot.";
      setRestoreToast({ tone: "error", message: msg, timestamp: Date.now() });
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  // On unmount, clear any pending timeout — we do NOT auto-fire the
  // delete here. If the user navigated away, the row will reappear on
  // next /dashboard load (we only mutated local state).
  useEffect(() => {
    return () => {
      if (pendingDeleteRef.current) {
        clearTimeout(pendingDeleteRef.current.timeoutId);
      }
    };
  }, []);

  // Per-session greeting from Pebble. Built after projects load so we
  // can reference the most-recently-built project by name. Computed in
  // useEffect (NOT during render) because:
  //   1. new Date() differs between SSR and CSR → hydration mismatch
  //   2. getUserProfile() reads sessionStorage — unavailable on the server
  //   3. `projects` is async — the greeting has to wait for the data
  // PebbleChat handles a greeting that arrives after mount via its own
  // greetingSetRef guard (see pebble-chat.tsx).
  const [greeting, setGreeting] = useState<string>("");
  const [chatContext, setChatContext] = useState<ChatProjectContext | null>(null);
  useEffect(() => {
    // Don't compute until the project list has settled — we want to
    // reference the most-recently-built project by name. If still
    // loading, bail early; the effect will re-run when loading → false.
    if (loading) return;

    const firstName = getUserProfile().firstName || null;
    const mostRecent = [...projects]
      .sort((a, b) => (b.built_at || "").localeCompare(a.built_at || ""))
      .find(Boolean) ?? null;

    setGreeting(
      buildGreeting({
        firstName,
        mostRecentProjectName: mostRecent?.business_name ?? null,
      }),
    );

    // Chat context — gives Pebble knowledge of the most-recently-built
    // project so it can answer project-specific questions and dispatch edits.
    setChatContext(
      mostRecent
        ? {
            slug:         mostRecent.slug,
            name:         mostRecent.business_name,
            industry:     mostRecent.business_type ?? undefined,
            design_dna:   mostRecent.design_dna ?? undefined,
            is_published: mostRecent.publish != null,
          }
        : null,
    );
  }, [user, loading, projects]);

  async function refresh() {
    setLoading(true);
    try {
      // Phase 45 (2026-05-22): subscription + usage are now read from
      // the shared DashboardSidebar (its own fetch); we only pull
      // projects + activity here. The Sidebar duplicates listProjects()
      // because it needs starred + recent slices for its drawer — a
      // single shared fetch would need a Provider; not worth it yet.
      const [projRes, activityRes] = await Promise.all([
        listProjects(),
        fetchActivity().catch(() => ({ activity: [], count: 0 })),
      ]);
      setProjects(projRes.projects);
      setActivity(activityRes.activity || []);
    } finally {
      setLoading(false);
    }
  }

  /** Fire the actual DELETE request and reconcile state. Called either
   *  by the 5s timer or immediately when a NEW delete pre-empts an
   *  in-flight one (edge case: user deletes B while A is still in the
   *  undo window — A flushes synchronously, B starts a fresh 5s). */
  async function flushDelete(p: PendingDelete) {
    try {
      await deleteProject(p.slug);
      void refresh();
    } catch {
      // Restore the row on API failure — same defensive behaviour as
      // the previous implementation.
      setProjects((prev) => {
        if (prev.some((x) => x.slug === p.slug)) return prev;
        return [p.project, ...prev];
      });
    }
  }

  function handleConfirmDelete(slug: string) {
    const project = projects.find((x) => x.slug === slug);
    if (!project) { setDeleting(null); return; }

    // If a previous delete is still pending, flush it now (fire the
    // request, drop the toast) before queuing the new one.
    const existing = pendingDeleteRef.current;
    if (existing) {
      clearTimeout(existing.timeoutId);
      void flushDelete(existing);
      pendingDeleteRef.current = null;
    }

    // Optimistically yank the row.
    setProjects((p) => p.filter((x) => x.slug !== slug));
    setDeleting(null);

    const startedAt = Date.now();
    const timeoutId = setTimeout(() => {
      // Only flush if THIS pending is still the active one (guards
      // against a race where the user undid + re-deleted the same slug
      // — the old timer would otherwise wipe the restored row).
      const current = pendingDeleteRef.current;
      if (current && current.slug === slug && current.startedAt === startedAt) {
        pendingDeleteRef.current = null;
        setPendingDelete(null);
        void flushDelete(current);
      }
    }, 5000);

    setPendingDelete({
      slug,
      business_name: project.business_name,
      project,
      timeoutId,
      startedAt,
    });
  }

  function handleUndoDelete() {
    const current = pendingDeleteRef.current;
    if (!current) return;
    clearTimeout(current.timeoutId);
    pendingDeleteRef.current = null;
    // Restore the row — guard against duplicates if the projects list
    // was refreshed externally while the toast was up.
    setProjects((prev) => {
      if (prev.some((x) => x.slug === current.slug)) return prev;
      return [current.project, ...prev];
    });
    setPendingDelete(null);
  }

  async function handleToggleStar(slug: string, currentlyStarred: boolean) {
    // Optimistic update so the chip flips instantly.
    setProjects((prev) => prev.map((p) => p.slug === slug ? { ...p, starred: !currentlyStarred } : p));
    try {
      await toggleStar(slug, !currentlyStarred);
    } catch {
      // Revert on failure
      setProjects((prev) => prev.map((p) => p.slug === slug ? { ...p, starred: currentlyStarred } : p));
    }
  }

  function openProject(p: ProjectSummary) {
    router.push(`/workspace/${encodeURIComponent(p.slug)}`);
  }

  // Filter + search
  const filtered = projects.filter((p) => {
    if (filter === "starred" && !p.starred) return false;
    if (filter === "recents") {
      // "recents" = top 6 by built_at — handled by slicing after sort
    }
    if (query.trim()) {
      const q = query.trim().toLowerCase();
      const hit =
        p.business_name.toLowerCase().includes(q) ||
        p.slug.toLowerCase().includes(q) ||
        (p.business_type || "").toLowerCase().includes(q);
      if (!hit) return false;
    }
    return true;
  });
  const visible = filter === "recents" ? filtered.slice(0, 6) : filtered;

  // Hydration-safe display name. getUserProfile() reads from sessionStorage,
  // which is empty on the server — so rendering `${firstName}` during SSR
  // and then again after client mount caused "Welcome back!" → "Welcome back,
  // Marc!" mismatch warnings. Defer the name to a post-mount render so the
  // server HTML and the first client render agree.
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);
  const displayName = mounted
    ? (getUserProfile().firstName || user?.email?.split("@")[0] || "")
    : "";

  // First-visit welcome card — dismissed via localStorage so it never
  // returns for the same browser. Initial state is `false` so SSR and
  // first client render agree (the card slides in post-mount). We hide
  // it entirely if the user already has projects: the card is empty-
  // state hand-holding, not perpetual UI noise.
  const ONBOARDED_KEY = "pebble.onboarded.v1";
  const [showOnboardCard, setShowOnboardCard] = useState(false);
  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const dismissed = window.localStorage.getItem(ONBOARDED_KEY);
      if (!dismissed) setShowOnboardCard(true);
    } catch {
      // localStorage blocked (private mode / Safari ITP): skip the card.
    }
  }, []);
  function dismissOnboardCard() {
    setShowOnboardCard(false);
    try { window.localStorage.setItem(ONBOARDED_KEY, String(Date.now())); } catch {}
  }

  // TopNav right slot — Marc's 2026-05-23 mockup: "+ New project"
  // button (primary, jumps into the welcome flow) + notification bell
  // with badge. Both surface on every dashboard-shell route so the
  // primary actions never go missing as the user navigates around.
  const topRightSlot = (
    <div className="flex items-center gap-2">
      <Link
        href="/workspace#phase=welcome"
        className={`${interactions.button} inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-primary text-primary-foreground text-sm font-semibold hover:opacity-90 transition-opacity`}
      >
        <Plus className="w-4 h-4" />
        New project
      </Link>
      <NotificationBell />
    </div>
  );

  return (
    <div className="flex flex-col h-screen-safe">
      <TopNav projectName="Dashboard" rightSlot={topRightSlot} />
      <div className="flex-1 min-h-0">
      <ControlCenter greeting={greeting} projectContext={chatContext} leftSidebar={<DashboardSidebar />}>
      <div className="p-6 md:p-8">
        <div className="max-w-5xl mx-auto space-y-6">
          {/* First-visit welcome card — shows only on a genuinely empty
              dashboard for a non-dismissed user. Once dismissed,
              localStorage flag suppresses it forever for this browser.
              Mounted ABOVE the page header so it's the first thing the
              user sees on their very first /dashboard load. */}
          {showOnboardCard && !loading && projects.length === 0 && (
            <OnboardingCard onDismiss={dismissOnboardCard} />
          )}

          {/* Page header — Linear-style: just the page title + live
              stats subtitle. Compact, data-forward, no emoji.
              2026-05-25 redesign. */}
          <header>
            <h1 className={`${type.dashboard.display.m} text-foreground`}>Projects</h1>
            <p className={`${type.body.s} text-muted-foreground mt-0.5`}>
              {loading ? "Loading…" : (
                <>
                  {mounted && displayName ? `${displayName}'s workspace` : "Your workspace"}
                  {!loading && projects.length > 0 && ` · ${projects.length} ${projects.length === 1 ? "project" : "projects"}`}
                  {!loading && projects.filter((p) => p.starred).length > 0 && ` · ${projects.filter((p) => p.starred).length} starred`}
                  {!loading && projects.filter((p) => p.publish != null).length > 0 && ` · ${projects.filter((p) => p.publish != null).length} published`}
                </>
              )}
            </p>
          </header>
          {/* Phase 45 — page-local filter chips sit in the main area now
              (not the sidebar). The sidebar is shared across workspace
              pages and shouldn't carry per-page state. These three chips
              are the same All / Starred / Recents view as before. */}
          <div className="flex items-center gap-3 flex-wrap">
            <FilterChip active={filter === "all"}     onClick={() => setFilter("all")}     Icon={Home}  label="All" />
            <FilterChip active={filter === "starred"} onClick={() => setFilter("starred")} Icon={Star}  label="Starred" />
            <FilterChip active={filter === "recents"} onClick={() => setFilter("recents")} Icon={Clock} label="Recents" />
            <div className="relative">
              <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search projects…"
                className="pl-9 pr-4 py-2 bg-card border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ring w-52"
              />
            </div>
          </div>

          {/* Home tiles — sit above the project grid on /dashboard so the
              page feels like a living surface, not just a folder. Three
              actions wired to real destinations:
                · Templates  → /templates  (browse + clone, instant starts)
                · Community  → /community  (showcase + partner + affiliate)
                · Guides     → /learn      (placeholder — see footnote)
              Marc's 2026-05-23 brief: Home should be the most energetic,
              welcoming surface. These tiles + the inbox of designs below
              accomplish the "interactive Home" ask without forcing a
              blog/CMS investment up front. /learn lands on a friendly
              "coming soon" stub for now — easy to replace with real
              content (or a remote-loaded post feed) without touching
              this surface again.
              Only renders on filter="all" (the Home view); Starred and
              Recents views hide it so they stay focused on the slice. */}
          {!loading && filter === "all" && (
            <HomeTiles hasProjects={projects.length > 0} />
          )}

          {loading && (
            <div className="text-center py-20 text-muted-foreground">Loading…</div>
          )}

          {!loading && visible.length === 0 && (
            <EmptyState filter={filter} query={query} />
          )}

          <motion.div
            initial="hidden"
            animate="visible"
            variants={{ hidden: {}, visible: { transition: { staggerChildren: 0.04 } } }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
          >
            <AnimatePresence>
              {visible.map((p) => (
                <ProjectCard
                  key={p.slug}
                  p={p}
                  onOpen={() => openProject(p)}
                  onToggleStar={() => handleToggleStar(p.slug, p.starred)}
                  onRequestDelete={() => setDeleting(p.slug)}
                  deletePending={deleting === p.slug}
                  onConfirmDelete={() => handleConfirmDelete(p.slug)}
                  onCancelDelete={() => setDeleting(null)}
                />
              ))}
            </AnimatePresence>
          </motion.div>

          {!loading && activity.length > 0 && (
            <ActivityFeed
              activity={activity}
              onOpenProject={(slug) => {
                const p = projects.find((x) => x.slug === slug);
                if (p) openProject(p);
              }}
              onRestore={handleRestoreFromActivity}
            />
          )}
        </div>
      </div>
      </ControlCenter>
      </div>

      {/* Gmail-style undo toast — only one pending delete at a time. */}
      <DeleteUndoToast pending={pendingDelete} onUndo={handleUndoDelete} />

      {/* Restore-from-activity toast — auto-dismisses; success variant
          carries a link to open the workspace at the restored slug. */}
      <RestoreToast toast={restoreToast} onOpen={(slug) => {
        const p = projects.find((x) => x.slug === slug);
        if (p) openProject(p);
      }} onDismiss={() => setRestoreToast(null)} />
    </div>
  );
}

// ---------------------------------------------------------------------------
// DeleteUndoToast — fixed-position bottom toast with a 5s progress bar.
// Mounted once at the page root; `pending` prop drives in/out.
// ---------------------------------------------------------------------------

function DeleteUndoToast({
  pending,
  onUndo,
}: {
  pending: { slug: string; business_name: string; startedAt: number } | null;
  onUndo: () => void;
}) {
  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-[60] pointer-events-none">
      <AnimatePresence>
        {pending && (
          <motion.div
            key={`${pending.slug}-${pending.startedAt}`}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 16 }}
            transition={{ duration: 0.2 }}
            className="pointer-events-auto bg-foreground text-background rounded-xl shadow-xl px-4 py-3 flex items-center gap-4 max-w-md overflow-hidden relative"
            role="status"
            aria-live="polite"
          >
            <Trash2 className="w-4 h-4 shrink-0 opacity-80" />
            <div className="flex-1 text-sm">
              Deleted <span className="font-semibold">{pending.business_name}</span>.
            </div>
            <button
              onClick={onUndo}
              className="flex items-center gap-1 text-sm font-bold uppercase tracking-wider text-primary hover:underline shrink-0"
            >
              <Undo2 className="w-3.5 h-3.5" /> Undo
            </button>
            {/* 5s progress bar at the bottom — purely visual. The actual
                timer lives in the parent's setTimeout. */}
            <motion.div
              key={`bar-${pending.slug}-${pending.startedAt}`}
              initial={{ width: "100%" }}
              animate={{ width: "0%" }}
              transition={{ duration: 5, ease: "linear" }}
              className="absolute bottom-0 left-0 h-0.5 bg-primary/70"
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ---------------------------------------------------------------------------
// OnboardingCard — one-time welcome card for users on their very first
// dashboard visit (no projects yet, not dismissed). Three quick-start
// CTAs cover the three on-ramps: Ask Pebble (the new-project flow),
// Templates (clone a proven starting point), Settings (account setup).
// Dismissal is persisted in localStorage under `pebble.onboarded.v1` —
// the card never returns for this browser once dismissed.
// ---------------------------------------------------------------------------

function OnboardingCard({ onDismiss }: { onDismiss: () => void }) {
  return (
    <div className="rounded-2xl border border-border bg-card p-6 md:p-8 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h2 className={`${type.dashboard.heading.l} text-foreground`}>
            Welcome to Pebble <span aria-hidden>👋</span>
          </h2>
          <p className={`${type.body.s} text-muted-foreground mt-2 max-w-xl`}>
            Pebble turns a sentence into a real website. Here are 3 quick
            ways to start:
          </p>
        </div>
        <button
          type="button"
          onClick={onDismiss}
          className="text-xs text-muted-foreground hover:text-foreground transition-colors underline shrink-0"
        >
          Got it, hide this
        </button>
      </div>
      <ul className="mt-5 grid grid-cols-1 md:grid-cols-3 gap-3">
        <li>
          <Link
            href="/workspace#phase=welcome"
            className="group flex items-start gap-3 rounded-xl border border-border bg-background p-4 hover:border-primary/40 hover:bg-accent/40 transition-colors h-full"
          >
            <Sparkles className="w-5 h-5 text-primary shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-foreground">Ask Pebble to build a site</p>
              <p className="text-xs text-muted-foreground mt-1">
                Start asking <span className="inline-block group-hover:translate-x-0.5 transition-transform" aria-hidden>→</span>
              </p>
            </div>
          </Link>
        </li>
        <li>
          <Link
            href="/templates"
            className="group flex items-start gap-3 rounded-xl border border-border bg-background p-4 hover:border-primary/40 hover:bg-accent/40 transition-colors h-full"
          >
            <Compass className="w-5 h-5 text-primary shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-foreground">Browse industry-tested templates</p>
              <p className="text-xs text-muted-foreground mt-1">
                See templates <span className="inline-block group-hover:translate-x-0.5 transition-transform" aria-hidden>→</span>
              </p>
            </div>
          </Link>
        </li>
        <li>
          <Link
            href="/settings"
            className="group flex items-start gap-3 rounded-xl border border-border bg-background p-4 hover:border-primary/40 hover:bg-accent/40 transition-colors h-full"
          >
            <Users className="w-5 h-5 text-primary shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-foreground">Configure your account</p>
              <p className="text-xs text-muted-foreground mt-1">
                Open settings <span className="inline-block group-hover:translate-x-0.5 transition-transform" aria-hidden>→</span>
              </p>
            </div>
          </Link>
        </li>
      </ul>
    </div>
  );
}

// ---------------------------------------------------------------------------
// HomeTiles — clean quick-action row above the project grid.
// 2026-05-25 redesign: replaced gradient blob promos with flat icon-chip
// action tiles. No decorative gradients — the icon background + border
// carry the affordance. Clean, Linear/Vercel-style.
// ---------------------------------------------------------------------------

const PEBBLE_TIPS = [
  "Cmd-K opens the command palette from anywhere in the workspace.",
  "Star a design to pin it to the sidebar — great for the one you're showing investors.",
  "Hit the version-history icon any time — every refinement is undoable.",
  "Click any element on the preview to edit its text, color, or size in place.",
  "Drop in a section from the gallery when you want a new block without writing a brief.",
  "Custom domain only takes one DNS record — Setup walks you through it.",
];

function HomeTiles({ hasProjects }: { hasProjects: boolean }) {
  const [tipIdx, setTipIdx] = useState(0);
  useEffect(() => {
    setTipIdx(Math.floor(Math.random() * PEBBLE_TIPS.length));
  }, []);

  return (
    <section className="space-y-3">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
        <ActionTile
          href="/templates"
          Icon={Compass}
          label="Browse templates"
          description={hasProjects ? "More starting points" : "Skip the blank page"}
        />
        <ActionTile
          href="/community/launchpad"
          Icon={Sparkles}
          label="Get inspired"
          description="See what others built"
        />
        <ActionTile
          href="/community"
          Icon={Users}
          label="Community"
          description="Meet other builders"
        />
      </div>
      {/* Rotating tip — single row, no card border */}
      <div className="flex items-center gap-2.5">
        <span className="text-[10px] uppercase tracking-widest font-bold text-primary shrink-0">Tip</span>
        <span className="text-muted-foreground/30" aria-hidden>·</span>
        <p className="text-xs text-muted-foreground flex-1 truncate">{PEBBLE_TIPS[tipIdx]}</p>
        <button
          type="button"
          onClick={() => setTipIdx((i) => (i + 1) % PEBBLE_TIPS.length)}
          className="text-xs text-muted-foreground hover:text-foreground transition-colors px-2 py-1 rounded-md hover:bg-accent shrink-0"
          aria-label="Next tip"
        >
          Next →
        </button>
      </div>
    </section>
  );
}

// ActionTile — flat bordered tile, icon-chip + label + arrow.
// No gradients. Clean affordance from border-on-hover + icon background.
function ActionTile({
  href, Icon, label, description,
}: {
  href: string;
  Icon: typeof Home;
  label: string;
  description: string;
}) {
  return (
    <Link
      href={href}
      className="group flex items-center gap-3 rounded-xl border border-border bg-card px-4 py-3.5 hover:bg-accent/40 hover:border-primary/30 transition-colors"
    >
      <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0 group-hover:bg-primary/15 transition-colors">
        <Icon className="w-4 h-4 text-primary" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-foreground leading-none">{label}</p>
        <p className="text-xs text-muted-foreground mt-0.5 truncate">{description}</p>
      </div>
      <ArrowRight className="w-3.5 h-3.5 text-muted-foreground/50 group-hover:text-foreground group-hover:translate-x-0.5 transition-all shrink-0" />
    </Link>
  );
}

// ---------------------------------------------------------------------------

function FilterChip({
  active, onClick, Icon, label,
}: {
  active: boolean;
  onClick: () => void;
  Icon: typeof Home;
  label: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`${interactions.chip} inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-semibold ${
        active
          ? "bg-primary/15 text-primary"
          : "bg-card border border-border text-muted-foreground hover:text-foreground"
      }`}
    >
      <Icon className="w-3.5 h-3.5" />
      {label}
    </button>
  );
}

// ---------------------------------------------------------------------------

function ActivityFeed({
  activity, onOpenProject, onRestore,
}: {
  activity: ActivityRow[];
  onOpenProject: (slug: string) => void;
  onRestore: (row: ActivityRow) => void;
}) {
  return (
    <section className="pt-4 border-t border-border space-y-4">
      <div className="flex items-center gap-2">
        <Clock className="w-4 h-4 text-muted-foreground" />
        <h2 className={`${type.eyebrow} text-foreground`}>Recently changed</h2>
        <p className={type.caption}>— hover a row to undo a refinement or edit in place.</p>
      </div>
      <ul className="space-y-1.5">
        {activity.slice(0, 10).map((row) => (
          <li
            key={`${row.slug}-${row.snapshot_id}`}
            className={`${interactions.card} group flex items-center justify-between gap-3 p-3 rounded-lg bg-card border border-border cursor-pointer`}
            onClick={() => onOpenProject(row.slug)}
            tabIndex={0}
          >
            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold text-foreground truncate">
                {row.business_name}
              </p>
              <p className={`${type.caption} truncate`}>
                {labelForReason(row.reason)} · {formatRelative(row.written_at)}
              </p>
            </div>
            <div className="flex items-center gap-3 shrink-0">
              {/* Restore button — visible on row hover only; keyboard
                  users always see it via focus-within fallback. Click
                  stops propagation so the row's "open project" doesn't
                  also fire. */}
              <button
                type="button"
                onClick={(e) => { e.stopPropagation(); onRestore(row); }}
                className="opacity-0 group-hover:opacity-100 focus-visible:opacity-100 transition-opacity inline-flex items-center gap-1 text-xs font-semibold text-primary hover:underline px-2 py-1 rounded"
                aria-label={`Restore ${row.business_name} to this snapshot`}
                title="Restore this snapshot"
              >
                <Undo2 className="w-3.5 h-3.5" />
                Restore
              </button>
              <span className={`${type.mono} text-muted-foreground`}>
                {row.files_count} files
              </span>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}

// ---------------------------------------------------------------------------
// RestoreToast — feedback for inline rollback from ActivityFeed.
// Success variant carries an "Open workspace" link. Auto-dismisses in 5s
// (timer lives in the parent). Mirrors DeleteUndoToast's layout for
// visual continuity.
// ---------------------------------------------------------------------------

function RestoreToast({
  toast, onOpen, onDismiss,
}: {
  toast: { tone: "success" | "error"; message: string; slug?: string; timestamp: number } | null;
  onOpen: (slug: string) => void;
  onDismiss: () => void;
}) {
  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-[60] pointer-events-none">
      <AnimatePresence>
        {toast && (
          <motion.div
            key={`restore-${toast.timestamp}`}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 16 }}
            transition={{ duration: 0.2 }}
            className={`pointer-events-auto rounded-xl shadow-xl px-4 py-3 flex items-center gap-4 max-w-md ${
              toast.tone === "success"
                ? "bg-foreground text-background"
                : "bg-destructive text-destructive-foreground"
            }`}
            role="status"
            aria-live="polite"
          >
            <Undo2 className="w-4 h-4 shrink-0 opacity-80" />
            <div className="flex-1 text-sm">{toast.message}</div>
            {toast.tone === "success" && toast.slug && (
              <button
                onClick={() => { onOpen(toast.slug!); onDismiss(); }}
                className="text-sm font-bold uppercase tracking-wider text-primary hover:underline shrink-0"
              >
                Open
              </button>
            )}
            <button
              onClick={onDismiss}
              className="text-xs opacity-70 hover:opacity-100 shrink-0"
              aria-label="Dismiss"
            >
              ✕
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function labelForReason(reason: string): string {
  if (reason.startsWith("refine")) return `Refinement: ${reason.replace("refine-", "")}`;
  if (reason.startsWith("visual-edit")) return `Visual edit: ${reason.replace("visual-edit-", "")}`;
  if (reason === "generate") return "Generated";
  if (reason === "restore") return "Restored";
  if (reason === "publish") return "Published";
  return reason;
}

function formatRelative(iso: string): string {
  if (!iso) return "";
  try {
    const t = new Date(iso).getTime();
    if (Number.isNaN(t)) return iso;
    const seconds = Math.floor((Date.now() - t) / 1000);
    if (seconds < 60)     return "just now";
    if (seconds < 3600)   return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400)  return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  } catch { return iso; }
}

// ---------------------------------------------------------------------------

function SidebarItem({
  active,
  onClick,
  Icon,
  label,
  count,
}: {
  active: boolean;
  onClick: () => void;
  Icon: typeof Home;
  label: string;
  count?: number;
}) {
  return (
    <button
      onClick={onClick}
      className={`${interactions.chip} flex items-center justify-between gap-2 px-3 py-2 rounded-lg text-sm font-semibold ${
        active
          ? "bg-primary/15 text-primary"
          : "text-muted-foreground hover:text-foreground"
      }`}
    >
      <span className="flex items-center gap-2">
        <Icon className="w-4 h-4" />
        {label}
      </span>
      {typeof count === "number" && (
        <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${active ? "bg-primary/30" : "bg-muted"}`}>
          {count}
        </span>
      )}
    </button>
  );
}

function ProjectCard({
  p,
  onOpen,
  onToggleStar,
  onRequestDelete,
  deletePending,
  onConfirmDelete,
  onCancelDelete,
}: {
  p: ProjectSummary;
  onOpen: () => void;
  onToggleStar: () => void;
  onRequestDelete: () => void;
  deletePending: boolean;
  onConfirmDelete: () => void;
  onCancelDelete: () => void;
}) {
  return (
    <motion.div
      variants={{
        hidden:  { opacity: 0, y: 12 },
        visible: { opacity: 1, y: 0 },
      }}
      exit={{ opacity: 0, scale: 0.96 }}
      // 2026-05-24 de-card-ify: dropped border-on-rest. The hero image
      // is now the dominant element; the card identity comes from
      // overflow-hidden + rounded-2xl + hover ring (instead of a
      // permanent border ringing every project). Reads as Spotify-
      // album-grid rather than data-tile-catalog.
      className={`${interactions.card} bg-card rounded-2xl overflow-hidden flex flex-col cursor-pointer relative group ring-1 ring-transparent hover:ring-primary/30 transition-shadow shadow-sm hover:shadow-md`}
      onClick={() => !deletePending && onOpen()}
      tabIndex={0}
    >
      {/* Hero image — pulled from the engine's post-build screenshot.
          Falls back to a DNA-tinted gradient block when the screenshot
          isn't ready yet (in-flight build) or pre-dates the
          screenshot pipeline. 2026-05-23. */}
      <ProjectHero p={p} />

      {/* Top-right actions sit over the hero corner so they don't
          push the title around. */}
      <div className="absolute top-3 right-3 flex items-center gap-1 z-10">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onToggleStar();
          }}
          className={`${interactions.iconButton} w-8 h-8 rounded-full flex items-center justify-center bg-card/85 backdrop-blur-sm border border-border/60`}
          aria-label={p.starred ? "Unstar" : "Star"}
        >
          <Star
            className={`w-4 h-4 transition-colors ${p.starred ? "fill-spark text-spark" : "text-muted-foreground"}`}
          />
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onRequestDelete();
          }}
          className="w-8 h-8 rounded-full flex items-center justify-center bg-card/85 backdrop-blur-sm border border-border/60 hover:bg-destructive/10 hover:text-destructive transition-colors text-muted-foreground"
          aria-label="Delete project"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      <div className="p-5 flex-1 flex flex-col gap-3">
      <div className="flex-1 min-w-0">
        <h3 className={`${type.dashboard.heading.m} text-foreground truncate`}>
          {p.business_name}
        </h3>
        {p.business_type && (
          <p className={`${type.mono} text-muted-foreground mt-1`}>
            {p.business_type.replace(/_/g, " ")}
          </p>
        )}
      </div>

      <div className="flex flex-wrap gap-2">
        {p.publish && (
          <a
            href={p.publish.url}
            target={p.publish.kind === "cloudflare" ? "_blank" : undefined}
            rel="noopener"
            download={p.publish.kind === "zip"}
            onClick={(e) => e.stopPropagation()}
            className="flex items-center gap-2 text-xs px-2.5 py-1.5 rounded-lg bg-earth/10 text-earth-deep border border-earth/30 hover:bg-earth/20 transition-colors"
            title={p.publish.kind === "cloudflare" ? "Live on Cloudflare" : "Download published ZIP"}
          >
            {p.publish.kind === "cloudflare" ? <Globe className="w-3 h-3" /> : <Download className="w-3 h-3" />}
            <span className="font-semibold">
              {p.publish.kind === "cloudflare" ? "Live" : "Published (ZIP)"}
            </span>
          </a>
        )}
        {p.domain && (
          <span
            onClick={(e) => e.stopPropagation()}
            className={`flex items-center gap-2 text-xs px-2.5 py-1.5 rounded-lg border ${
              p.domain.status === "active"
                ? "bg-spark/10 text-spark-deep border-spark/30"
                : p.domain.status === "error"
                  ? "bg-destructive/10 text-destructive border-destructive/30"
                  : "bg-muted text-muted-foreground border-border"
            }`}
            title={p.domain.host}
          >
            <Globe className="w-3 h-3" />
            <span className="font-semibold truncate max-w-[14ch]">{p.domain.host}</span>
            <span className="text-[10px] opacity-70 uppercase">
              {p.domain.status === "active" ? "live" : p.domain.status === "error" ? "error" : "DNS pending"}
            </span>
          </span>
        )}
        {p.inbox && p.inbox.total > 0 && (
          <Link
            href={`/inbox?slug=${encodeURIComponent(p.slug)}`}
            onClick={(e) => e.stopPropagation()}
            className="flex items-center gap-2 text-xs px-2.5 py-1.5 rounded-lg bg-primary/10 text-primary border border-primary/30 hover:bg-primary/20 transition-colors"
            title="Open inbox"
          >
            <Mail className="w-3 h-3" />
            <span className="font-semibold">
              {p.inbox.unread > 0 ? `${p.inbox.unread} new` : `${p.inbox.total} read`}
            </span>
          </Link>
        )}
      </div>

      <div className="flex items-center justify-between pt-2 border-t border-border">
        <p className={type.caption}>
          {p.file_count} {p.file_count === 1 ? "file" : "files"}
          {p.design_dna && ` · ${p.design_dna.replace(/_/g, " ")}`}
        </p>
        <a
          href={p.preview_url}
          target="_blank"
          rel="noopener"
          onClick={(e) => e.stopPropagation()}
          className={`${interactions.link} ${type.caption} text-primary flex items-center gap-1`}
        >
          Preview <ExternalLink className="w-3 h-3" />
        </a>
      </div>
      </div>

      {/* Inline delete confirmation — fewer modals = faster to undo your mind */}
      <AnimatePresence>
        {deletePending && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={(e) => e.stopPropagation()}
            className="absolute inset-0 bg-card/95 backdrop-blur-sm rounded-2xl border border-destructive/40 flex flex-col items-center justify-center text-center p-5 gap-3"
          >
            <Trash2 className="w-6 h-6 text-destructive" />
            <p className={`${type.dashboard.heading.m} text-foreground`}>Delete {p.business_name}?</p>
            <p className={`${type.caption} -mt-1`}>All snapshots and files are removed permanently.</p>
            <div className="flex gap-2 mt-1">
              <button
                onClick={onCancelDelete}
                className={`${interactions.button} bg-card border border-border text-foreground px-4 py-2 rounded-lg text-sm font-semibold`}
              >
                Keep it
              </button>
              <button
                onClick={onConfirmDelete}
                className={`${interactions.button} bg-destructive text-destructive-foreground px-4 py-2 rounded-lg text-sm font-semibold`}
              >
                Delete
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// 2026-05-23: Hero image for project cards. Pulls from the engine's
// /api/projects/<slug>/screenshot endpoint, which serves the post-
// build Playwright capture. Falls back to a DNA-tinted gradient so
// in-flight builds (no screenshot yet) and old projects from before
// the screenshot pipeline still look intentional rather than broken.
function ProjectHero({ p }: { p: ProjectSummary }) {
  const [errored, setErrored] = useState(false);
  const showImage = p.screenshot_url && !errored;

  // DNA-tinted gradient palette — picks a deterministic two-color
  // stop based on the DNA name so each project's fallback is at
  // least unique within the grid. Matches no specific design DNA
  // color tokens — these are just visual filler.
  const dnaSlug = (p.design_dna || p.slug).toLowerCase();
  const palettes: Array<[string, string]> = [
    ["#1e293b", "#475569"], // slate
    ["#1a1a2e", "#16213e"], // navy
    ["#3a1c1c", "#5c2c2c"], // burgundy
    ["#1c2e1a", "#2c5c2c"], // forest
    ["#2c1c3a", "#4a2c5c"], // plum
    ["#3a2e1a", "#5c4a2c"], // amber
  ];
  const idx = Math.abs(
    dnaSlug.split("").reduce((acc, c) => acc + c.charCodeAt(0), 0)
  ) % palettes.length;
  const [c1, c2] = palettes[idx];

  return (
    <div
      className="relative aspect-[16/10] w-full overflow-hidden bg-muted"
      style={{
        background: !showImage
          ? `linear-gradient(135deg, ${c1}, ${c2})`
          : undefined,
      }}
    >
      {showImage && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={p.screenshot_url!}
          alt={`${p.business_name} preview`}
          className="absolute inset-0 w-full h-full object-cover object-top transition-transform duration-500 group-hover:scale-105"
          loading="lazy"
          onError={() => setErrored(true)}
        />
      )}
      {!showImage && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <p
            className="text-2xl font-bold text-white/70 px-4 text-center truncate max-w-[80%]"
            style={{ textShadow: "0 1px 2px rgba(0,0,0,0.3)" }}
          >
            {p.business_name}
          </p>
        </div>
      )}
      {/* Bottom gradient so the title underneath always has contrast */}
      <div className="absolute inset-x-0 bottom-0 h-1/3 bg-gradient-to-t from-card/40 to-transparent pointer-events-none" />
    </div>
  );
}

function EmptyState({ filter, query }: { filter: Filter; query: string }) {
  if (query) {
    return (
      <div className="text-center py-16">
        <Search className="w-10 h-10 mx-auto mb-3 text-muted-foreground/40" />
        <p className={`${type.dashboard.heading.l} text-foreground`}>No matches for &ldquo;{query}&rdquo;.</p>
        <p className={`${type.body.s} text-muted-foreground mt-2`}>Try a different name or industry.</p>
      </div>
    );
  }
  if (filter === "starred") {
    return (
      <div className="text-center py-16">
        <Star className="w-10 h-10 mx-auto mb-3 text-muted-foreground/40" />
        <p className={`${type.dashboard.heading.l} text-foreground`}>Nothing starred yet.</p>
        <p className={`${type.body.s} text-muted-foreground mt-2`}>Click the star icon on any project to keep it handy.</p>
      </div>
    );
  }
  // Cinematic empty state — centered metallic P hero + Recent Activity rail.
  // Marc 2026-05-25 v2: rebuilt to match the design ref. The P is the
  // focal point (god-ray light shafts, particle field, asset slot at
  // /dashboard/metallic-p.png with CSS fallback). The Activity rail
  // grounds the page so it doesn't feel like a screensaver.
  return (
    <div className="grid grid-cols-1 lg:grid-cols-[1fr_280px] gap-6 py-4">
      {/* ── CENTER: Cinematic P hero ── */}
      <DashboardEmptyHero />

      {/* ── RIGHT: Recent Activity rail ── */}
      <DashboardActivityRail />
    </div>
  );
}

// ── DashboardEmptyHero — centered metallic P + light shafts + CTAs ──
function DashboardEmptyHero() {
  // The dramatic visual — metallic P + light shafts + star particles —
  // is the user's design ref cropped to just the spotlight region.
  // It spans the full container width (no max-w cap) so it reads as a
  // proper hero, not a contained card. Real text + buttons render below
  // it on a matching dark continuation. No CSS approximation; the image
  // IS the design.
  return (
    <div className="relative rounded-3xl overflow-hidden bg-[#1a1d20] flex flex-col items-center justify-start">
      {/* Hero image — full container width */}
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src="/dashboard/hero-bg.png"
        alt=""
        aria-hidden="true"
        className="w-full h-auto select-none pointer-events-none block"
        // @ts-expect-error fetchpriority is valid HTML but not in React typedefs yet
        fetchpriority="high"
      />

      {/* Copy + CTAs — rendered below the image on continuation of dark bg */}
      <div className="text-center max-w-2xl w-full px-6 pt-6 pb-12">
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-3 tracking-tight">
          No projects created yet.
        </h2>
        <p className="text-base md:text-lg text-white/60 mb-10 max-w-md mx-auto">
          Ready to start building? Create your first website or explore templates.
        </p>
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-center gap-4">
          <Link
            href="/workspace#phase=welcome"
            className="inline-flex items-center justify-center gap-2.5 px-8 py-4 rounded-full bg-white text-black text-base font-semibold shadow-2xl hover:bg-white/90 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/60"
          >
            <Plus className="w-5 h-5" /> Start something new
          </Link>
          <Link
            href="/templates"
            className="inline-flex items-center justify-center gap-2.5 px-8 py-4 rounded-full bg-white/5 border border-white/30 text-white/90 text-base font-semibold backdrop-blur-sm hover:bg-white/10 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/60"
          >
            <Search className="w-5 h-5" /> Browse templates
          </Link>
        </div>
      </div>
    </div>
  );
}

// ── DashboardActivityRail — Recent Activity panel ──
function DashboardActivityRail() {
  // Placeholder seed data — when real audit-log integration ships, this
  // hook can swap to fetching from the audit-log API.
  const items = [
    { label: "User logged in",   meta: "1 minute ago" },
    { label: "Viewed templates", meta: "1 hour ago" },
    { label: "Settings updated", meta: "Yesterday" },
  ];
  return (
    <aside className="rounded-2xl border border-border bg-card p-5 h-fit">
      <h3 className={`${type.dashboard.heading.m} text-foreground mb-4`}>
        Recent Activity
      </h3>
      <ul className="space-y-3">
        {items.map((it) => (
          <li key={it.label} className="flex flex-col">
            <span className={`${type.body.s} text-foreground`}>{it.label}</span>
            <span className={`${type.caption} text-muted-foreground`}>{it.meta}</span>
          </li>
        ))}
      </ul>
    </aside>
  );
}
