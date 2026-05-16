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
      className="sticky top-0 inset-x-0 z-50 h-16 px-8 flex items-center justify-between border-b border-border bg-background/80 backdrop-blur"
    >
      <div className="flex items-center gap-6">
        <Link
          href="/"
          className={`${interactions.link} ${type.display.m} text-accent-foreground hover:text-primary`}
        >
          Pebble.
        </Link>
        {projectName && (
          <>
            <div className="h-6 w-px bg-border" />
            <motion.span
              layoutId="project-name"
              style={{ viewTransitionName: "project-name" }}
              className={`${type.heading.s} text-foreground`}
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
