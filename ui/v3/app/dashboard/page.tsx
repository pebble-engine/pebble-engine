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
  Coins,
  Globe,
  Download,
} from "lucide-react";
import { TopNav } from "@/components/top-nav";
import {
  listProjects,
  toggleStar,
  fetchUsage,
  deleteProject,
  type ProjectSummary,
  type UsageSummary,
} from "@/lib/api";
import { setLastBuild, getUserProfile } from "@/lib/state";

type Filter = "all" | "starred" | "recents";

export default function DashboardPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [usage, setUsage] = useState<UsageSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<Filter>("all");
  const [query, setQuery] = useState("");
  const [firstName, setFirstName] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null); // slug pending confirm

  useEffect(() => {
    setFirstName(getUserProfile().firstName || null);
    void refresh();
  }, []);

  async function refresh() {
    setLoading(true);
    try {
      const [projRes, usageRes] = await Promise.all([listProjects(), fetchUsage().catch(() => null)]);
      setProjects(projRes.projects);
      setUsage(usageRes);
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
    // Pretend the user just generated this so workspace routes work.
    setLastBuild({
      slug: p.slug,
      preview_url: p.preview_url,
      saved_to: `output/${p.slug}/`,
      file_count: p.file_count,
    });
    router.push("/workspace");
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

  return (
    <div className="min-h-screen flex flex-col">
      <TopNav projectName="Projects" />

      <div className="flex flex-1">
        {/* Left sidebar — Pebble's "established company" surface */}
        <aside className="w-[240px] bg-card border-r border-border p-5 flex flex-col gap-1">
          <div className="mb-5 px-1">
            <p className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
              {firstName ? `${firstName}'s` : "Your"} workspace
            </p>
          </div>

          <SidebarItem
            active={filter === "all"}
            onClick={() => setFilter("all")}
            Icon={Home}
            label="All projects"
            count={projects.length}
          />
          <SidebarItem
            active={filter === "starred"}
            onClick={() => setFilter("starred")}
            Icon={Star}
            label="Starred"
            count={projects.filter((p) => p.starred).length}
          />
          <SidebarItem
            active={filter === "recents"}
            onClick={() => setFilter("recents")}
            Icon={Clock}
            label="Recents"
          />

          <div className="mt-auto pt-4 border-t border-border space-y-3">
            {/* Usage indicator — honest cost telemetry. Shows total only when
                we have at least one paid build to report. */}
            {usage && usage.projects > 0 && (
              <div className="px-3 py-2.5 bg-background border border-border rounded-lg">
                <div className="flex items-center gap-2 mb-1">
                  <Coins className="w-3.5 h-3.5 text-muted-foreground" />
                  <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
                    Estimated cost
                  </p>
                </div>
                <p className="font-display text-lg font-semibold text-foreground">
                  ${usage.total_estimated_cost_usd.toFixed(4)}
                </p>
                <p className="text-[10px] text-muted-foreground mt-0.5">
                  {usage.projects} {usage.projects === 1 ? "build" : "builds"} · {(usage.total_input_tokens + usage.total_output_tokens).toLocaleString()} tokens
                </p>
              </div>
            )}

            <Link
              href="/"
              className="flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2.5 rounded-lg text-sm font-semibold hover:opacity-90 transition-opacity"
            >
              <Plus className="w-4 h-4" />
              Start something new
            </Link>
          </div>
        </aside>

        {/* Main project grid */}
        <main className="flex-1 p-8 overflow-y-auto">
          <div className="max-w-5xl mx-auto space-y-6">
            <div className="flex items-center justify-between gap-4 flex-wrap">
              <div>
                <h1 className="font-display text-3xl font-bold text-foreground">
                  {filter === "starred" ? "Starred projects" : filter === "recents" ? "Recently built" : "All projects"}
                </h1>
                <p className="text-sm text-muted-foreground mt-1">
                  {visible.length} {visible.length === 1 ? "project" : "projects"}
                </p>
              </div>
              <div className="relative">
                <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input
                  type="search"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search by name or industry..."
                  className="pl-9 pr-4 py-2 bg-card border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ring w-72"
                />
              </div>
            </div>

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
          </div>
        </main>
      </div>
    </div>
  );
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
      className={`flex items-center justify-between gap-2 px-3 py-2.5 rounded-lg text-sm font-semibold transition-colors ${
        active
          ? "bg-primary/15 text-primary"
          : "text-muted-foreground hover:bg-accent hover:text-foreground"
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
      whileHover={{ y: -3 }}
      className="bg-card border border-border rounded-2xl p-5 flex flex-col gap-3 cursor-pointer relative group"
      onClick={() => !deletePending && onOpen()}
    >
      <div className="absolute top-3 right-3 flex items-center gap-1">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onToggleStar();
          }}
          className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-accent transition-colors"
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
          className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-destructive/10 hover:text-destructive transition-colors text-muted-foreground"
          aria-label="Delete project"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 min-w-0">
        <h3 className="font-display text-lg font-semibold text-foreground truncate pr-16">
          {p.business_name}
        </h3>
        {p.business_type && (
          <p className="text-xs font-mono uppercase tracking-wider text-muted-foreground mt-0.5">
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
            className="flex items-center gap-2 text-xs px-2.5 py-1.5 rounded-lg bg-earth/10 text-earth border border-earth/30 hover:bg-earth/20 transition-colors"
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
                ? "bg-spark/10 text-spark border-spark/30"
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
      </div>

      <div className="flex items-center justify-between pt-2 border-t border-border">
        <p className="text-[11px] text-muted-foreground">
          {p.file_count} {p.file_count === 1 ? "file" : "files"}
          {p.design_dna && ` · ${p.design_dna.replace(/_/g, " ")}`}
        </p>
        <a
          href={p.preview_url}
          target="_blank"
          rel="noopener"
          onClick={(e) => e.stopPropagation()}
          className="text-[11px] text-primary hover:underline flex items-center gap-1"
        >
          Preview <ExternalLink className="w-3 h-3" />
        </a>
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
            <p className="font-display text-base font-semibold text-foreground">Delete {p.business_name}?</p>
            <p className="text-xs text-muted-foreground -mt-1">All snapshots and files are removed permanently.</p>
            <div className="flex gap-2 mt-1">
              <button
                onClick={onCancelDelete}
                className="bg-card border border-border text-foreground px-4 py-1.5 rounded-lg text-sm font-semibold hover:bg-accent"
              >
                Keep it
              </button>
              <button
                onClick={onConfirmDelete}
                className="bg-destructive text-destructive-foreground px-4 py-1.5 rounded-lg text-sm font-semibold hover:opacity-90"
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

function EmptyState({ filter, query }: { filter: Filter; query: string }) {
  if (query) {
    return (
      <div className="text-center py-16">
        <p className="font-display text-2xl text-foreground">No matches for &ldquo;{query}&rdquo;.</p>
        <p className="text-muted-foreground mt-2">Try a different name or industry.</p>
      </div>
    );
  }
  if (filter === "starred") {
    return (
      <div className="text-center py-16">
        <Star className="w-10 h-10 mx-auto text-muted-foreground mb-4" />
        <p className="font-display text-2xl text-foreground">Nothing starred yet.</p>
        <p className="text-muted-foreground mt-2">Click the star icon on any project to keep it handy.</p>
      </div>
    );
  }
  return (
    <div className="text-center py-20">
      <p className="font-display text-2xl text-foreground">Nothing here yet.</p>
      <p className="text-muted-foreground mt-2 mb-6">Let&apos;s build your first site.</p>
      <Link
        href="/"
        className="inline-flex items-center gap-2 bg-primary text-primary-foreground px-5 py-2.5 rounded-full text-sm font-semibold hover:opacity-90 transition-opacity"
      >
        <Plus className="w-4 h-4" /> Start something new
      </Link>
    </div>
  );
}
