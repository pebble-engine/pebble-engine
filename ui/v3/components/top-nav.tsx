"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowLeft, LifeBuoy, Plus, Pencil, Sparkles } from "lucide-react";
import { ThemeToggle } from "./theme-toggle";
import { AuthMenu } from "./auth-menu";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";

/**
 * Shared top nav for every screen after welcome. Brand mark left, theme
 * toggle + Help + auth right. Keep this minimal — anything more complex
 * (project names, device toggles) belongs to the workspace shell.
 *
 * The project-name slot carries `layoutId="project-name"` so framer-motion
 * morphs it from the welcome hero's matching label on the welcome →
 * workspace transition. The viewTransitionName mirrors the same identity
 * for the Chrome / Edge / Safari native morph path.
 *
 * 2026-05-20 Phase 15a: project name is now click-to-edit + "+ New"
 * button starts a fresh project (clears sessionStorage). Marc kept
 * landing on "Untitled Project" with prior chips pre-selected.
 */
export function TopNav({
  projectName,
  rightSlot,
  onProjectNameChange,
  onNewProject,
}: {
  projectName?: string;
  rightSlot?: React.ReactNode;
  /** Called when the user edits the project name inline. */
  onProjectNameChange?: (next: string) => void;
  /** Called when the user clicks "+ New" to start a fresh project. */
  onNewProject?: () => void;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(projectName ?? "");
  const inputRef = useRef<HTMLInputElement>(null);

  // 2026-05-24 — universal back affordance. Users hit secondary pages
  // (community sub-routes, integrations, settings, /workspace/<slug>,
  // legal pages, help) with no obvious way back to where they came from.
  // Browser back works but isn't visible on the page. This is the
  // explicit UI version.
  //
  // Hidden on the "root" surfaces the sidebar already gets users to:
  // the landing, the dashboard home base, auth pages (those have their
  // own flows), and /workspace's welcome phase (the prompt entry hero
  // shouldn't have a back button competing with the Build CTA).
  const router = useRouter();
  const pathname = usePathname() || "";
  const NO_BACK_PATHS = new Set([
    "/", "/dashboard", "/login", "/signup", "/forgot", "/reset",
  ]);
  // /workspace without a slug is the welcome-phase entry — no back. But
  // /workspace/<slug> (deep-linked into an existing project) SHOULD show
  // back so users can return to the dashboard list.
  const showBack = !NO_BACK_PATHS.has(pathname) && pathname !== "/workspace";

  const handleBack = () => {
    // history.length > 1 means there's somewhere to go back to. The
    // initial-load case (user opened the link in a new tab) falls
    // through to /dashboard as a sensible home.
    if (typeof window !== "undefined" && window.history.length > 1) {
      router.back();
    } else {
      router.push("/dashboard");
    }
  };

  // Keep local draft in sync when the parent's projectName changes
  // (e.g. on a new project or after a rename elsewhere).
  useEffect(() => {
    if (!editing) setDraft(projectName ?? "");
  }, [projectName, editing]);

  useEffect(() => {
    if (editing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [editing]);

  const commit = () => {
    const next = draft.trim() || "New project";
    if (onProjectNameChange && next !== projectName) {
      onProjectNameChange(next);
    }
    setEditing(false);
  };

  const cancel = () => {
    setDraft(projectName ?? "");
    setEditing(false);
  };

  return (
    <header
      style={{ viewTransitionName: "top-nav" }}
      className="sticky top-0 inset-x-0 z-50 h-16 px-4 sm:px-8 flex items-center justify-between gap-2 border-b border-white/10 bg-black/60 backdrop-blur-xl font-[family-name:var(--font-plus-jakarta-sans)]"
    >
      <div className="flex items-center gap-3 sm:gap-4 min-w-0">
        {showBack && (
          <button
            type="button"
            onClick={handleBack}
            aria-label="Back"
            title="Back"
            className={`${interactions.iconButton} inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-full text-sm text-white/75 hover:text-white hover:bg-white/10 transition-colors`}
          >
            <ArrowLeft className="w-4 h-4" aria-hidden />
            <span className="hidden md:inline">Back</span>
          </button>
        )}
        <Link
          href="/"
          className="inline-flex items-center px-3 py-1.5 rounded-full bg-stone-900/40 backdrop-blur-xl border border-white/15 text-lg font-semibold"
        >
          <span className="bg-gradient-to-b from-white via-white to-[#b4c0ff] bg-clip-text text-transparent">
            Pebble.
          </span>
        </Link>
        {projectName && (
          <>
            <div className="h-5 w-px bg-white/15" />
            {editing ? (
              <input
                ref={inputRef}
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onBlur={commit}
                onKeyDown={(e) => {
                  if (e.key === "Enter") commit();
                  if (e.key === "Escape") cancel();
                }}
                maxLength={80}
                className="bg-transparent text-base font-medium text-white/95 outline-none border-b border-white/40 focus:border-white px-1 min-w-[200px]"
                aria-label="Project name"
              />
            ) : (
              <button
                type="button"
                onClick={() => onProjectNameChange && setEditing(true)}
                className="group inline-flex items-center gap-2 text-base font-medium text-white/85 hover:text-white transition-colors"
                title={onProjectNameChange ? "Click to rename" : undefined}
              >
                <motion.span
                  layoutId="project-name"
                  style={{ viewTransitionName: "project-name" }}
                >
                  {projectName}
                </motion.span>
                {onProjectNameChange && (
                  <Pencil className="w-3.5 h-3.5 opacity-0 group-hover:opacity-60 transition-opacity" aria-hidden />
                )}
              </button>
            )}
          </>
        )}
        {onNewProject && (
          <>
            <div className="h-5 w-px bg-white/15" />
            <button
              type="button"
              onClick={onNewProject}
              className={`${interactions.chip} inline-flex items-center gap-1.5 text-sm text-white/70 hover:text-white px-2 py-1 rounded-md`}
              title="Start a new project (clears current answers)"
            >
              <Plus className="w-3.5 h-3.5" aria-hidden />
              <span className={type.label}>New</span>
            </button>
          </>
        )}
      </div>
      <div className="flex items-center gap-2 sm:gap-3 shrink-0">
        {rightSlot}
        <Link
          href="/templates"
          title="Browse templates"
          className={`${interactions.chip} inline-flex items-center gap-1.5 text-sm text-white/70 hover:text-white px-2 py-1 rounded-md`}
        >
          <Sparkles className="w-3.5 h-3.5" aria-hidden />
          <span className={`${type.label} hidden sm:inline`}>Templates</span>
        </Link>
        <Link
          href="/help"
          title="Help"
          aria-label="Help"
          className={`${interactions.iconButton} w-10 h-10 rounded-full flex items-center justify-center text-muted-foreground hover:text-foreground`}
        >
          <LifeBuoy className="w-5 h-5" />
        </Link>
        <AuthMenu />
        <ThemeToggle />
      </div>
    </header>
  );
}
