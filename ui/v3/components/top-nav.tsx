"use client";

import Link from "next/link";
import { ThemeToggle } from "./theme-toggle";

/**
 * Shared top nav for every screen after welcome. Brand mark left, theme
 * toggle + Help right. Keep this minimal — anything more complex (project
 * names, device toggles) belongs to the workspace shell.
 */
export function TopNav({
  projectName,
  rightSlot,
}: {
  projectName?: string;
  rightSlot?: React.ReactNode;
}) {
  return (
    <header className="sticky top-0 inset-x-0 z-50 h-16 px-8 flex items-center justify-between border-b border-border bg-background/80 backdrop-blur">
      <div className="flex items-center gap-6">
        <Link
          href="/"
          className="font-display text-2xl font-bold tracking-tight text-accent-foreground hover:text-primary transition-colors"
        >
          Pebble.
        </Link>
        {projectName && (
          <>
            <div className="h-6 w-px bg-border" />
            <span className="text-base font-semibold text-foreground">{projectName}</span>
          </>
        )}
      </div>
      <div className="flex items-center gap-3">
        {rightSlot}
        <ThemeToggle />
      </div>
    </header>
  );
}
