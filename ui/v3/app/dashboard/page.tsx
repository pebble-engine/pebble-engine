"use client";

import { useEffect, useState } from "react";
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
  FolderOpen,
  Search,
  Sparkles,
  Compass,
  Users,
  BookOpen,
  ArrowRight,
} from "lucide-react";
import { TopNav } from "@/components/top-nav";
import { ControlCenter } from "@/components/control-center";
import { DashboardSidebar } from "@/components/workspace/dashboard-sidebar";
import { PebletMascot } from "@/components/peblet-mascot";
import { NotificationBell } from "@/components/notification-bell";
import { useAuth } from "@/components/auth-provider";
import { getUserProfile } from "@/lib/state";
import { type } from "@/lib/type";
import {
  listProjects,
  toggleStar,
  fetchActivity,
  deleteProject,
  type ProjectSummary,
  type ActivityRow,
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

  useEffect(() => {
    void refresh();
  }, []);

  // 2026-05-23: Per-session greeting from Pebble. Computed once at
  // mount so the assistant introduces itself when the user lands on
  // the dashboard, then the conversation continues from there. Uses
  // the local profile first-name when known so it feels personal,
  // falls back to a clean generic when not.
  const greeting = (() => {
    const name = (typeof window !== "undefined" ? getUserProfile().firstName : "") || "";
    const hour = new Date().getHours();
    const tod = hour < 12 ? "morning" : hour < 18 ? "afternoon" : "evening";
    if (name) return `Good ${tod}, ${name}. I'm Pebble — your AI assistant. Want me to take you somewhere, or should I tell you what's new?`;
    if (user) return `Good ${tod}. I'm Pebble — your AI assistant. Ask me to navigate, explain something, or help you take action.`;
    return "Hi, I'm Pebble. Sign in and I'll help you build, navigate, and manage your sites.";
  })();

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

  async function handleDelete(slug: string) {
    // Optimistic remove
    const prev = projects;
    setProjects((p) => p.filter((x) => x.slug !== slug));
    setDeleting(null);
    try {
      await deleteProject(slug);
      void refresh();  // refresh usage totals too
    } catch {
      // Restore on failure
      setProjects(prev);
    }
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

  const profile = typeof window !== "undefined" ? getUserProfile() : { firstName: "" };
  const displayName = profile.firstName || (user?.email?.split("@")[0]) || "";

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
      <ControlCenter greeting={greeting} leftSidebar={<DashboardSidebar />}>
      <div className="p-6 md:p-8">
        <div className="max-w-5xl mx-auto space-y-6">
          {/* Welcome banner — Marc's 2026-05-23 mockup: warm header
              with a wave emoji + tagline that anchors the page as
              "your home base" rather than "a folder of designs." */}
          <header className="space-y-1">
            <p className="text-sm font-semibold text-muted-foreground">
              Welcome back{displayName ? `, ${displayName}` : ""}! <span aria-hidden>👋</span>
            </p>
            <h1 className={`${type.display.m} text-foreground`}>Dashboard</h1>
            <p className={`${type.body.s} text-muted-foreground`}>
              Here&apos;s what&apos;s happening with your projects.
            </p>
          </header>
          {/* Phase 45 — page-local filter chips sit in the main area now
              (not the sidebar). The sidebar is shared across workspace
              pages and shouldn't carry per-page state. These three chips
              are the same All / Starred / Recents view as before. */}
          <div className="flex items-center justify-between gap-4 flex-wrap">
            <div>
              <h2 className={`${type.heading.l} text-foreground`}>
                {filter === "starred" ? "Starred" : filter === "recents" ? "Recently built" : "Your projects"}
              </h2>
              <p className={`${type.body.s} text-muted-foreground mt-1`}>
                {loading
                  ? "Loading your projects…"
                  : `${visible.length} ${visible.length === 1 ? "project" : "projects"}`}
              </p>
            </div>
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
                  placeholder="Search by name or industry..."
                  className="pl-9 pr-4 py-2 bg-card border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ring w-60"
                />
              </div>
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
                  onConfirmDelete={() => handleDelete(p.slug)}
                  onCancelDelete={() => setDeleting(null)}
                />
              ))}
            </AnimatePresence>
          </motion.div>

          {!loading && activity.length > 0 && (
            <ActivityFeed activity={activity} onOpenProject={(slug) => {
              const p = projects.find((x) => x.slug === slug);
              if (p) openProject(p);
            }} />
          )}
        </div>
      </div>
      </ControlCenter>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// HomeTiles — interactive Home-section content for /dashboard.
//
// Three persistent action cards (Templates / Get inspired / Pebble guides)
// plus one rotating "tip of the day" so the surface doesn't feel static.
// Marc's 2026-05-23 brief: "Home section and community section need to be
// the most energetic, welcoming." This is the first energy beat — a
// dense, color-forward strip above the project grid that gives the user
// somewhere to go BESIDES their own designs.
//
// Why tile + rotating tip rather than a full blog feed: a real CMS is a
// project on its own. The tile pattern gets the right energy on screen
// today without committing to authored content. When we DO start writing
// articles, the third tile points at /learn and that page can grow into
// the feed without touching the dashboard again.
//
// When the user has no projects yet, the first tile gently nudges
// toward Templates (faster way to ship than building from scratch).
// When they have projects, all three tiles stay the same — we don't
// hide them after first build, because returning to ideas / tips is
// what makes the dashboard a habit.
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
  // Per-mount tip pick — refreshes every dashboard visit so the same
  // tip doesn't stare back at the user every time.
  const [tipIdx, setTipIdx] = useState(0);
  useEffect(() => {
    setTipIdx(Math.floor(Math.random() * PEBBLE_TIPS.length));
  }, []);

  return (
    <section className="space-y-3">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <HomeTile
          href="/templates"
          Icon={Compass}
          eyebrow="Templates"
          title={hasProjects ? "Start from a proven shape" : "Skip the blank page"}
          body="Browse cinematic, industry-tuned starting points. One click clones and customizes for your business."
          accent="from-[#3054ff]/15 to-[#3054ff]/0"
        />
        <HomeTile
          href="/community/launchpad"
          Icon={Sparkles}
          eyebrow="Get inspired"
          title="See what others built"
          body="Real sites from the Pebble community. Steal the structure, swap in your story."
          accent="from-amber-500/15 to-amber-500/0"
        />
        <HomeTile
          href="/community"
          Icon={Users}
          eyebrow="Community"
          title="Meet other builders"
          body="Affiliates, partners, launch help. Connect with people building alongside you."
          accent="from-emerald-500/15 to-emerald-500/0"
        />
      </div>

      {/* Rotating tip strip — small dose of interactivity. Cycles on
          dashboard mount; no autoplay timer so it doesn't pull focus
          from the project grid below. */}
      <div className="flex items-center gap-3 px-4 py-3 rounded-xl border border-border bg-card/60">
        <BookOpen className="w-4 h-4 text-muted-foreground shrink-0" />
        <p className="text-sm text-muted-foreground flex-1">
          <span className="text-foreground font-semibold">Pebble tip</span>
          <span className="mx-2 opacity-40">·</span>
          {PEBBLE_TIPS[tipIdx]}
        </p>
        <button
          type="button"
          onClick={() => setTipIdx((i) => (i + 1) % PEBBLE_TIPS.length)}
          className="text-xs text-muted-foreground hover:text-foreground transition-colors px-2 py-1 rounded-md hover:bg-accent"
          aria-label="Show another Pebble tip"
        >
          Next →
        </button>
      </div>
    </section>
  );
}

function HomeTile({
  href, Icon, eyebrow, title, body, accent,
}: {
  href: string;
  Icon: typeof Home;
  eyebrow: string;
  title: string;
  body: string;
  /** Tailwind gradient-from / gradient-to fragment, e.g. "from-blue-500/15 to-blue-500/0". */
  accent: string;
}) {
  return (
    <Link
      href={href}
      className={`${interactions.card} group relative overflow-hidden rounded-xl border border-border bg-card p-5 flex flex-col gap-3 hover:border-primary/40 transition-colors`}
    >
      <div className={`absolute inset-0 -z-0 bg-gradient-to-br ${accent} opacity-100 group-hover:opacity-100 transition-opacity`} />
      <div className="relative z-10 flex items-center gap-2">
        <Icon className="w-4 h-4 text-foreground" />
        <span className="text-[11px] uppercase tracking-widest font-semibold text-muted-foreground">
          {eyebrow}
        </span>
      </div>
      <div className="relative z-10 flex flex-col gap-1.5">
        <h3 className="text-base font-bold text-foreground leading-tight">{title}</h3>
        <p className="text-sm text-muted-foreground leading-snug">{body}</p>
      </div>
      <div className="relative z-10 mt-auto inline-flex items-center gap-1.5 text-sm font-semibold text-foreground/80 group-hover:text-foreground transition-colors">
        Open <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
      </div>
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
  activity, onOpenProject,
}: { activity: ActivityRow[]; onOpenProject: (slug: string) => void }) {
  return (
    <section className="pt-4 border-t border-border space-y-4">
      <div className="flex items-center gap-2">
        <Clock className="w-4 h-4 text-muted-foreground" />
        <h2 className={`${type.eyebrow} text-foreground`}>Recently changed</h2>
        <p className={type.caption}>— every refinement and edit, undoable from the project workspace.</p>
      </div>
      <ul className="space-y-1.5">
        {activity.slice(0, 10).map((row) => (
          <li
            key={`${row.slug}-${row.snapshot_id}`}
            className={`${interactions.card} flex items-center justify-between gap-3 p-3 rounded-lg bg-card border border-border cursor-pointer`}
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
            <span className={`${type.mono} text-muted-foreground shrink-0`}>
              {row.files_count} files
            </span>
          </li>
        ))}
      </ul>
    </section>
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
      className={`${interactions.card} bg-card border border-border rounded-2xl overflow-hidden flex flex-col cursor-pointer relative group`}
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
        <h3 className={`${type.heading.m} text-foreground truncate`}>
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
            <p className={`${type.heading.m} text-foreground`}>Delete {p.business_name}?</p>
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
        <p className={`${type.heading.l} text-foreground`}>No matches for &ldquo;{query}&rdquo;.</p>
        <p className={`${type.body.s} text-muted-foreground mt-2`}>Try a different name or industry.</p>
      </div>
    );
  }
  if (filter === "starred") {
    return (
      <div className="text-center py-16">
        <Star className="w-10 h-10 mx-auto mb-3 text-muted-foreground/40" />
        <p className={`${type.heading.l} text-foreground`}>Nothing starred yet.</p>
        <p className={`${type.body.s} text-muted-foreground mt-2`}>Click the star icon on any project to keep it handy.</p>
      </div>
    );
  }
  // Funny all-empty state — Marc 2026-05-23: "add a funny landing
  // area where it says 'Boy it sure does look empty in here' or
  // something like that when they delete all projects or have an
  // empty folder." Peblet mascot + warm copy + clear next-step CTA.
  return (
    <div className="text-center py-16 px-6 rounded-2xl border border-dashed border-border bg-card/50">
      <div className="mb-4 flex justify-center">
        <PebletMascot size="md" animate />
      </div>
      <p className={`${type.heading.l} text-foreground`}>
        Boy, it sure does look empty in here.
      </p>
      <p className={`${type.body.s} text-muted-foreground mt-2 mb-6 max-w-sm mx-auto`}>
        Want to fix that together? I can walk you through your first build, or you can pick a template and customize it.
      </p>
      <div className="flex flex-wrap items-center justify-center gap-2">
        <Link
          href="/workspace#phase=welcome"
          className={`${interactions.button} inline-flex items-center gap-2 bg-primary text-primary-foreground px-5 py-2 rounded-full text-sm font-semibold`}
        >
          <Plus className="w-4 h-4" /> Start something new
        </Link>
        <Link
          href="/templates"
          className={`${interactions.button} inline-flex items-center gap-2 bg-card border border-border text-foreground px-5 py-2 rounded-full text-sm font-semibold`}
        >
          Browse templates
        </Link>
      </div>
    </div>
  );
}
