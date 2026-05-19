"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { LifeBuoy } from "lucide-react";
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
 */
export function TopNav({
  projectName,
  rightSlot,
}: {
  projectName?: string;
  rightSlot?: React.ReactNode;
}) {
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
            <motion.span
              layoutId="project-name"
              style={{ viewTransitionName: "project-name" }}
              className="text-base font-medium text-white/85"
            >
              {projectName}
            </motion.span>
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
