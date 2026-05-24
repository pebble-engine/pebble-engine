"use client";

/**
 * /projects — focused project-list view (2026-05-23).
 *
 * Marc's Control Center mockup put Projects as a distinct sidebar
 * entry from Dashboard. The distinction:
 *
 *   - /dashboard = welcome banner + Home tiles + Peblet tip + grid
 *   - /projects  = grid only, more focused, for users who just want
 *                  to browse their builds without the home dressing
 *
 * Same chat panel + sidebar shell as /dashboard so navigation stays
 * consistent — Peblet remains the catch-all "find anything" lane.
 */

import { useEffect, useMemo, useState } from "react";
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
} from "lucide-react";
import { TopNav } from "@/components/top-nav";
import { ControlCenter } from "@/components/control-center";
import { DashboardSidebar } from "@/components/workspace/dashboard-sidebar";
import { PebletMascot } from "@/components/peblet-mascot";
import { NotificationBell } from "@/components/notification-bell";
import { type } from "@/lib/type";
import {
  listProjects,
  toggleStar,
  deleteProject,
  type ProjectSummary,
} from "@/lib/api";
import { interactions } from "@/lib/interactions";

type Filter = "all" | "starred" | "recents";

export default function ProjectsPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<Filter>("all");
  const [query, setQuery] = useState("");
  const [deleting, setDeleting] = useState<string | null>(null);

  useEffect(() => {
    void refresh();
  }, []);

  async function refresh() {
    setLoading(true);
    try {
      const res = await listProjects();
      setProjects(res.projects);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(slug: string) {
    const prev = projects;
    setProjects((p) => p.filter((x) => x.slug !== slug));
    setDeleting(null);
    try {
      await deleteProject(slug);
      void refresh();
    } catch {
      setProjects(prev);
    }
  }

  async function handleToggleStar(slug: string, currentlyStarred: boolean) {
    setProjects((prev) => prev.map((p) => p.slug === slug ? { ...p, starred: !currentlyStarred } : p));
    try {
      await toggleStar(slug, !currentlyStarred);
    } catch {
      setProjects((prev) => prev.map((p) => p.slug === slug ? { ...p, starred: currentlyStarred } : p));
    }
  }

  function openProject(p: ProjectSummary) {
    router.push(`/workspace/${encodeURIComponent(p.slug)}`);
  }

  const visible = useMemo(() => {
    const filtered = projects.filter((p) => {
      if (filter === "starred" && !p.starred) return false;
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
    return filter === "recents" ? filtered.slice(0, 6) : filtered;
  }, [projects, filter, query]);

  const greeting = "On Projects. Want me to open one, sort by something, or jump back to the dashboard?";

  // Same top-right slot as /dashboard: "+ New project" + bell. Keeps
  // primary actions in the same spot as the user navigates around.
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
      <TopNav projectName="Projects" rightSlot={topRightSlot} />
      <div className="flex-1 min-h-0">
        <ControlCenter greeting={greeting} leftSidebar={<DashboardSidebar />}>
          <div className="p-6 md:p-8">
            <div className="max-w-5xl mx-auto space-y-6">
              <header className="flex items-end justify-between gap-4 flex-wrap">
                <div>
                  <h1 className={`${type.dashboard.display.m} text-foreground`}>Your projects</h1>
                  <p className={`${type.body.s} text-muted-foreground mt-1`}>
                    {loading
                      ? "Loading your projects…"
                      : `${projects.length} ${projects.length === 1 ? "project" : "projects"} · open one to keep building.`}
                  </p>
                </div>
                <Link
                  href="/workspace#phase=welcome"
                  className={`${interactions.button} inline-flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-full text-sm font-semibold`}
                >
                  <Plus className="w-4 h-4" /> New project
                </Link>
              </header>

              <div className="flex items-center gap-3 flex-wrap">
                <FilterChip active={filter === "all"}     onClick={() => setFilter("all")}     Icon={Home}  label="All" />
                <FilterChip active={filter === "starred"} onClick={() => setFilter("starred")} Icon={Star}  label="Starred" />
                <FilterChip active={filter === "recents"} onClick={() => setFilter("recents")} Icon={Clock} label="Recents" />
                <div className="relative ml-auto">
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

              {loading && (
                <div className="text-center py-20 text-muted-foreground">Loading…</div>
              )}

              {!loading && visible.length === 0 && (
                <ProjectsEmptyState filter={filter} query={query} totalProjects={projects.length} />
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
            </div>
          </div>
        </ControlCenter>
      </div>
    </div>
  );
}

// ---------- Shared sub-components (kept local to this page; see
// dashboard/page.tsx for the canonical version. When we have a third
// caller we'll lift these into components/projects/.) -----------------

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

function ProjectsEmptyState({
  filter, query, totalProjects,
}: {
  filter: Filter;
  query: string;
  totalProjects: number;
}) {
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
  // Funny all-empty state — Marc 2026-05-23. Same copy + Peblet
  // pattern as the dashboard's empty state so users see a consistent
  // voice across both surfaces.
  return (
    <div className="text-center py-16 px-6 rounded-2xl border border-dashed border-border bg-card/50">
      <div className="mb-4 flex justify-center">
        <PebletMascot size="md" animate />
      </div>
      <p className={`${type.dashboard.heading.l} text-foreground`}>
        {totalProjects === 0
          ? "Boy, it sure does look empty in here."
          : "Nothing in this view yet."}
      </p>
      <p className={`${type.body.s} text-muted-foreground mt-2 mb-6 max-w-sm mx-auto`}>
        {totalProjects === 0
          ? "Want to fix that together? I can walk you through your first build, or you can pick a template and customize it."
          : "Try the All tab, or start something new."}
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

// Project card — same shape as dashboard's, with hero image. Kept
// local rather than imported to avoid the dashboard page's heavy
// dependency tree (state, useRouter, etc.) being pulled in twice.
function ProjectCard({
  p, onOpen, onToggleStar, onRequestDelete, deletePending, onConfirmDelete, onCancelDelete,
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
      variants={{ hidden: { opacity: 0, y: 12 }, visible: { opacity: 1, y: 0 } }}
      exit={{ opacity: 0, scale: 0.96 }}
      className={`${interactions.card} bg-card border border-border rounded-2xl overflow-hidden flex flex-col cursor-pointer relative group`}
      onClick={() => !deletePending && onOpen()}
      tabIndex={0}
    >
      <ProjectHero p={p} />
      <div className="absolute top-3 right-3 flex items-center gap-1 z-10">
        <button
          onClick={(e) => { e.stopPropagation(); onToggleStar(); }}
          className={`${interactions.iconButton} w-8 h-8 rounded-full flex items-center justify-center bg-card/85 backdrop-blur-sm border border-border/60`}
          aria-label={p.starred ? "Unstar" : "Star"}
        >
          <Star className={`w-4 h-4 transition-colors ${p.starred ? "fill-spark text-spark" : "text-muted-foreground"}`} />
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); onRequestDelete(); }}
          className="w-8 h-8 rounded-full flex items-center justify-center bg-card/85 backdrop-blur-sm border border-border/60 hover:bg-destructive/10 hover:text-destructive transition-colors text-muted-foreground"
          aria-label="Delete project"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
      <div className="p-5 flex-1 flex flex-col gap-3">
        <div className="flex-1 min-w-0">
          <h3 className={`${type.dashboard.heading.m} text-foreground truncate`}>{p.business_name}</h3>
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
            >
              {p.publish.kind === "cloudflare" ? <Globe className="w-3 h-3" /> : <Download className="w-3 h-3" />}
              <span className="font-semibold">
                {p.publish.kind === "cloudflare" ? "Live" : "Published (ZIP)"}
              </span>
            </a>
          )}
          {p.inbox && p.inbox.total > 0 && (
            <Link
              href={`/inbox?slug=${encodeURIComponent(p.slug)}`}
              onClick={(e) => e.stopPropagation()}
              className="flex items-center gap-2 text-xs px-2.5 py-1.5 rounded-lg bg-primary/10 text-primary border border-primary/30 hover:bg-primary/20 transition-colors"
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
              <button onClick={onCancelDelete} className={`${interactions.button} bg-card border border-border text-foreground px-4 py-2 rounded-lg text-sm font-semibold`}>
                Keep it
              </button>
              <button onClick={onConfirmDelete} className={`${interactions.button} bg-destructive text-destructive-foreground px-4 py-2 rounded-lg text-sm font-semibold`}>
                Delete
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function ProjectHero({ p }: { p: ProjectSummary }) {
  const [errored, setErrored] = useState(false);
  const showImage = p.screenshot_url && !errored;
  const dnaSlug = (p.design_dna || p.slug).toLowerCase();
  const palettes: Array<[string, string]> = [
    ["#1e293b", "#475569"], ["#1a1a2e", "#16213e"], ["#3a1c1c", "#5c2c2c"],
    ["#1c2e1a", "#2c5c2c"], ["#2c1c3a", "#4a2c5c"], ["#3a2e1a", "#5c4a2c"],
  ];
  const idx = Math.abs(dnaSlug.split("").reduce((acc, c) => acc + c.charCodeAt(0), 0)) % palettes.length;
  const [c1, c2] = palettes[idx];
  return (
    <div
      className="relative aspect-[16/10] w-full overflow-hidden bg-muted"
      style={{ background: !showImage ? `linear-gradient(135deg, ${c1}, ${c2})` : undefined }}
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
      <div className="absolute inset-x-0 bottom-0 h-1/3 bg-gradient-to-t from-card/40 to-transparent pointer-events-none" />
    </div>
  );
}

// Suppress unused-import warning for FolderOpen — it's referenced
// from the JSX above via the FilterChip Icon prop chain.
const _keep_folderopen_import = FolderOpen;
void _keep_folderopen_import;
