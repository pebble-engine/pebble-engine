"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import {
  Command, Home, Plus, Search, Star, Clock, LifeBuoy, Mail, Folder,
  LogOut, Shield,
} from "lucide-react";
import { listProjects, type ProjectSummary } from "@/lib/api";
import { setLastBuild } from "@/lib/state";
import { useAuth } from "@/components/auth-provider";

type Action = {
  id:       string;
  label:    string;
  hint?:    string;
  group:    "Navigate" | "Projects" | "Account";
  Icon:     typeof Command;
  run:      () => void;
  keywords?: string;
};

/** Global Ctrl/Cmd+K palette mounted via the root layout. */
export function CommandPalette() {
  const router = useRouter();
  const { user, signOut } = useAuth();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [active, setActive] = useState(0);
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  // Global hotkey
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      const isModifier = e.metaKey || e.ctrlKey;
      if (isModifier && (e.key === "k" || e.key === "K")) {
        e.preventDefault();
        setOpen((v) => !v);
      } else if (e.key === "Escape" && open) {
        setOpen(false);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  // Lazy-load projects when the palette opens (only first time)
  useEffect(() => {
    if (!open || projects.length > 0) return;
    listProjects().then((r) => setProjects(r.projects)).catch(() => {});
  }, [open, projects.length]);

  // Reset state when closing
  useEffect(() => {
    if (!open) {
      setQuery("");
      setActive(0);
    } else {
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [open]);

  const close = useCallback(() => setOpen(false), []);

  const baseActions = useMemo<Action[]>(() => {
    const nav: Action[] = [
      { id: "nav-home",      label: "Start a new site",  hint: "/",          group: "Navigate", Icon: Plus,      run: () => router.push("/") },
      { id: "nav-dashboard", label: "Dashboard",         hint: "/dashboard", group: "Navigate", Icon: Home,      run: () => router.push("/dashboard") },
      { id: "nav-starred",   label: "Starred projects",  hint: "/dashboard", group: "Navigate", Icon: Star,      run: () => router.push("/dashboard") },
      { id: "nav-recents",   label: "Recents",           hint: "/dashboard", group: "Navigate", Icon: Clock,     run: () => router.push("/dashboard") },
      { id: "nav-help",      label: "Help & FAQ",        hint: "/help",      group: "Navigate", Icon: LifeBuoy,  run: () => router.push("/help") },
      { id: "nav-admin",     label: "Admin tools",       hint: "/admin",     group: "Navigate", Icon: Shield,    run: () => router.push("/admin") },
    ];
    const acct: Action[] = user
      ? [{ id: "acct-signout", label: "Sign out", group: "Account", Icon: LogOut, run: async () => { await signOut(); router.push("/login"); } }]
      : [
          { id: "acct-signin",  label: "Sign in",  hint: "/login",  group: "Account", Icon: Home, run: () => router.push("/login") },
          { id: "acct-signup",  label: "Sign up",  hint: "/signup", group: "Account", Icon: Plus, run: () => router.push("/signup") },
        ];
    return [...nav, ...acct];
  }, [router, user, signOut]);

  const projectActions = useMemo<Action[]>(() => {
    const out: Action[] = [];
    for (const p of projects.slice(0, 30)) {
      out.push({
        id: `open-${p.slug}`,
        label: `Open ${p.business_name}`,
        hint: p.slug,
        group: "Projects",
        Icon: Folder,
        keywords: `${p.business_name} ${p.slug} ${p.business_type || ""}`,
        run: () => {
          setLastBuild({ slug: p.slug, preview_url: p.preview_url, saved_to: `output/${p.slug}/`, file_count: p.file_count });
          router.push("/workspace");
        },
      });
      if (p.inbox && p.inbox.total > 0) {
        out.push({
          id: `inbox-${p.slug}`,
          label: `Inbox: ${p.business_name}`,
          hint: `${p.inbox.unread} unread`,
          group: "Projects",
          Icon: Mail,
          keywords: `inbox messages ${p.business_name}`,
          run: () => router.push(`/inbox?slug=${encodeURIComponent(p.slug)}`),
        });
      }
    }
    return out;
  }, [projects, router]);

  const allActions = useMemo(() => [...baseActions, ...projectActions], [baseActions, projectActions]);

  // Filter on query — simple substring fuzzy
  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return allActions;
    return allActions.filter((a) =>
      a.label.toLowerCase().includes(q)
      || (a.hint || "").toLowerCase().includes(q)
      || (a.keywords || "").toLowerCase().includes(q)
    );
  }, [allActions, query]);

  // Group for display
  const grouped = useMemo(() => {
    const groups: Record<Action["group"], Action[]> = { Navigate: [], Projects: [], Account: [] };
    filtered.forEach((a) => groups[a.group].push(a));
    return groups;
  }, [filtered]);

  // Reset active on filter change
  useEffect(() => { setActive(0); }, [query, allActions.length]);

  const runActive = useCallback(() => {
    const a = filtered[active];
    if (!a) return;
    close();
    setTimeout(() => a.run(), 50);
  }, [filtered, active, close]);

  function onInputKey(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActive((i) => Math.min(filtered.length - 1, i + 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActive((i) => Math.max(0, i - 1));
    } else if (e.key === "Enter") {
      e.preventDefault();
      runActive();
    }
  }

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={close}
            className="fixed inset-0 bg-charcoal/40 backdrop-blur-sm z-[100]"
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.97, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.97, y: -10 }}
            transition={{ duration: 0.18, ease: [0.22, 1, 0.36, 1] }}
            className="fixed left-1/2 top-[15%] -translate-x-1/2 w-[min(640px,90vw)] z-[101] bg-card border border-border rounded-2xl shadow-2xl overflow-hidden"
          >
            <div className="flex items-center gap-3 px-4 h-14 border-b border-border">
              <Search className="w-5 h-5 text-muted-foreground" />
              <input
                ref={inputRef}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={onInputKey}
                placeholder="Search anything — projects, pages, settings…"
                className="flex-1 bg-transparent text-base text-foreground focus:outline-none"
              />
              <kbd className="hidden md:inline-flex font-mono text-[10px] px-1.5 py-0.5 bg-background border border-border rounded text-muted-foreground">
                Esc
              </kbd>
            </div>

            <div className="max-h-[60vh] overflow-y-auto py-2">
              {filtered.length === 0 && (
                <p className="px-4 py-8 text-sm text-muted-foreground text-center">No matches.</p>
              )}
              {(["Navigate", "Projects", "Account"] as const).map((group) => (
                grouped[group].length > 0 && (
                  <div key={group} className="mb-1">
                    <p className="px-4 py-1.5 text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
                      {group}
                    </p>
                    {grouped[group].map((a) => {
                      const idx = filtered.indexOf(a);
                      const isActive = idx === active;
                      return (
                        <button
                          key={a.id}
                          onMouseEnter={() => setActive(idx)}
                          onClick={() => { close(); setTimeout(() => a.run(), 50); }}
                          className={`w-full text-left px-4 py-2 flex items-center gap-3 transition-colors ${
                            isActive ? "bg-accent" : "hover:bg-accent/60"
                          }`}
                        >
                          <a.Icon className="w-4 h-4 text-muted-foreground shrink-0" />
                          <span className="text-sm text-foreground flex-1 truncate">{a.label}</span>
                          {a.hint && <span className="text-[11px] text-muted-foreground font-mono">{a.hint}</span>}
                        </button>
                      );
                    })}
                  </div>
                )
              ))}
            </div>

            <div className="px-4 h-9 border-t border-border flex items-center gap-3 text-[11px] text-muted-foreground bg-background">
              <span className="inline-flex items-center gap-1"><kbd className="font-mono px-1 bg-card border border-border rounded">↑↓</kbd> navigate</span>
              <span className="inline-flex items-center gap-1"><kbd className="font-mono px-1 bg-card border border-border rounded">↵</kbd> select</span>
              <span className="ml-auto inline-flex items-center gap-1"><Command className="w-3 h-3" />K to open</span>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
