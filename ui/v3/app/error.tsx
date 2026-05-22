"use client";

import { useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { InfiniteGrid } from "@/components/ui/the-infinite-grid";

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Let error monitoring (if added later) capture this.
    console.error("[pebble error boundary]", error);
  }, [error]);

  return (
    <InfiniteGrid className="min-h-screen-safe">
      <main className="relative z-10 flex flex-col items-center justify-center min-h-screen-safe text-center px-4 max-w-3xl mx-auto">
        <motion.span
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 0.06, scale: 1 }}
          transition={{ duration: 0.8 }}
          className="font-display text-[18vw] leading-none font-bold tracking-tight text-foreground -mb-8 select-none"
          aria-hidden="true"
        >
          500
        </motion.span>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="space-y-6"
        >
          <div className="space-y-3">
            <h1 className="font-display text-3xl md:text-4xl font-bold text-foreground">
              Something went sideways.
            </h1>
            <p className="text-lg text-muted-foreground max-w-md mx-auto">
              An unexpected error occurred. Your work is safe — nothing was deleted.
            </p>
            {error.digest && (
              <p className="text-xs text-muted-foreground font-mono">
                ref: {error.digest}
              </p>
            )}
          </div>

          <div className="flex flex-col sm:flex-row gap-3 justify-center pt-2">
            <button
              onClick={reset}
              className="bg-primary text-primary-foreground px-6 py-3 rounded-full font-semibold text-sm hover:opacity-90 transition-opacity"
            >
              Try again
            </button>
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
