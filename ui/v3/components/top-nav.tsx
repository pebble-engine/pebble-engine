"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { LifeBuoy, Plus, Pencil } from "lucide-react";
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
      className="sticky top-0 inset-x-0 z-50 h-16 px-8 flex items-center justify-between border-b border-white/10 bg-black/60 backdrop-blur-xl font-[family-name:var(--font-instrument-sans)]"
    >
      <div className="flex items-center gap-4">
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
      <div className="flex items-center gap-3">
        {rightSlot}
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
