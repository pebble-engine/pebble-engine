"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { InfiniteGrid } from "@/components/ui/the-infinite-grid";

/**
 * 404 — turn the dead end into a build prompt. Borrowed in concept from
 * Lovable's "this page doesn't exist yet — want to build it?" pattern,
 * reworded in Pebble's voice.
 */
export default function NotFound() {
  return (
    <InfiniteGrid className="min-h-screen-safe">
      <main className="relative z-10 flex flex-col items-center justify-center min-h-screen-safe text-center px-4 max-w-3xl mx-auto">
        <motion.span
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 0.08, scale: 1 }}
          transition={{ duration: 0.8 }}
          className="font-display-sans text-[18vw] leading-none font-bold tracking-tight text-foreground -mb-8 select-none"
          aria-hidden="true"
        >
          404
        </motion.span>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="space-y-6"
        >
          <div className="space-y-3">
            <h1 className="font-display-sans text-3xl md:text-4xl font-bold text-foreground">
              We haven&apos;t built this corner yet.
            </h1>
            <p className="text-lg text-muted-foreground max-w-md mx-auto">
              The page you&apos;re looking for doesn&apos;t exist. Want me to add it to your plan?
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 justify-center pt-2">
            <Link
              href="/"
              className="bg-primary text-primary-foreground px-6 py-3 rounded-full font-semibold text-sm hover:opacity-90 transition-opacity"
            >
              Start something new
            </Link>
            <Link
              href="/workspace"
              className="bg-card border border-border text-foreground px-6 py-3 rounded-full font-semibold text-sm hover:bg-accent transition-colors"
            >
              Back to my workspace
            </Link>
          </div>
        </motion.div>
      </main>
    </InfiniteGrid>
  );
}
