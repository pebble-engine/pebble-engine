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
} from "lucide-react";
import { TopNav } from "@/components/top-nav";
import { listProjects, toggleStar, type ProjectSummary } from "@/lib/api";
import { setLastBuild, getUserProfile } from "@/lib/state";

type Filter = "all" | "starred" | "recents";

export default function DashboardPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<Filter>("all");
  const [query, setQuery] = useState("");
  const [firstName, setFirstName] = useState<string | null>(null);

  useEffect(() => {
    setFirstName(getUserProfile().firstName || null);
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

          <div className="mt-auto pt-4 border-t border-border">
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
}: {
  p: ProjectSummary;
  onOpen: () => void;
  onToggleStar: () => void;
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
      onClick={onOpen}
    >
      <button
        onClick={(e) => {
          e.stopPropagation();
          onToggleStar();
        }}
        className="absolute top-3 right-3 w-8 h-8 rounded-full flex items-center justify-center hover:bg-accent transition-colors"
        aria-label={p.starred ? "Unstar" : "Star"}
      >
        <Star
          className={`w-4 h-4 transition-colors ${p.starred ? "fill-spark text-spark" : "text-muted-foreground"}`}
        />
      </button>

      <div className="flex-1 min-w-0">
        <h3 className="font-display text-lg font-semibold text-foreground truncate pr-8">
          {p.business_name}
        </h3>
        {p.business_type && (
          <p className="text-xs font-mono uppercase tracking-wider text-muted-foreground mt-0.5">
            {p.business_type.replace(/_/g, " ")}
          </p>
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
