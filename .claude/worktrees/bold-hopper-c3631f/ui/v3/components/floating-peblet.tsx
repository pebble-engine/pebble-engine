"use client";

/**
 * FloatingPeblet — draggable/collapsible Peblet chat widget.
 *
 * Mounts via React portal to document.body so it floats above all
 * page content. Replaces the fixed 340px ControlCenter right rail
 * on every non-workspace page.
 *
 * Position persists to localStorage ("peblet-widget-pos").
 * Defaults to bottom-right (24px margins) on first load.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { motion, AnimatePresence, useMotionValue } from "framer-motion";
import { MessageSquare, X } from "lucide-react";
import { PebbleChat } from "@/components/pebble-chat";
import { type ChatProjectContext } from "@/lib/api";

const STORAGE_KEY = "peblet-widget-pos";

function getSavedPos(): { x: number; y: number } | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const p = JSON.parse(raw) as { x: number; y: number };
    if (typeof p.x === "number" && typeof p.y === "number") return p;
  } catch {}
  return null;
}

export type FloatingPebletProps = {
  greeting?: string;
  projectContext?: ChatProjectContext | null;
};

export function FloatingPeblet({ greeting, projectContext }: FloatingPebletProps) {
  const [mounted, setMounted] = useState(false);
  const [open, setOpen] = useState(false);

  // useMotionValue avoids re-renders during drag. Initialised to 0,0
  // (safe for SSR); real position applied in useEffect after mount.
  const motionX = useMotionValue(0);
  const motionY = useMotionValue(0);

  // Track open state for handleDragEnd closure to avoid stale values.
  const openRef = useRef(false);

  // Distinguish drag-release from real click. Framer Motion fires onClick
  // on the inner button after onDragEnd, which would otherwise open the
  // panel every time the user drags. onDragStart only fires once the drag
  // threshold is crossed (~3px), so it reliably marks real drags.
  const wasDraggedRef = useRef(false);

  // Close button ref for focus management when panel opens.
  const closeBtnRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const saved = getSavedPos();
    const defaultPos = {
      x: window.innerWidth - 404,   // 380px panel + 24px margin
      y: window.innerHeight - 544,  // 520px panel + 24px margin
    };
    const p = saved ?? defaultPos;
    // Clamp to current viewport (using collapsed 64px dimensions)
    const clampedX = Math.max(20, Math.min(window.innerWidth - 64 - 20, p.x));
    const clampedY = Math.max(20, Math.min(window.innerHeight - 64 - 20, p.y));
    motionX.set(clampedX);
    motionY.set(clampedY);
    setMounted(true);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Focus the close button when panel opens for keyboard navigation.
  useEffect(() => {
    if (open && closeBtnRef.current) {
      closeBtnRef.current.focus();
    }
  }, [open]);

  function savePos(x: number, y: number) {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify({ x, y }));
    } catch {}
  }

  const handleDragEnd = useCallback(() => {
    const panelW = openRef.current ? 380 : 64;
    const panelH = openRef.current ? 520 : 64;
    const rawX = motionX.get();
    const rawY = motionY.get();
    const x = Math.max(20, Math.min(window.innerWidth - panelW - 20, rawX));
    const y = Math.max(20, Math.min(window.innerHeight - panelH - 20, rawY));
    motionX.set(x);
    motionY.set(y);
    savePos(x, y);
  }, [motionX, motionY]);

  if (!mounted) return null;

  return createPortal(
    <motion.div
      drag
      dragMomentum={false}
      style={{ x: motionX, y: motionY, position: "fixed", zIndex: 9999 }}
      onDragStart={() => {
        wasDraggedRef.current = true;
      }}
      onDragEnd={handleDragEnd}
      className="touch-none"
      role="complementary"
      aria-label="Peblet assistant"
    >
      <AnimatePresence mode="wait">
        {!open ? (
          /* ── Collapsed: 64×64 pill ── */
          <motion.button
            key="collapsed"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            transition={{ duration: 0.15 }}
            type="button"
            onClick={() => {
              // If this click is the tail of a drag, swallow it and reset.
              if (wasDraggedRef.current) {
                wasDraggedRef.current = false;
                return;
              }
              setOpen(true);
              openRef.current = true;
            }}
            aria-label="Open Peblet assistant"
            className="relative w-16 h-16 rounded-full bg-foreground text-background shadow-2xl flex items-center justify-center hover:scale-105 transition-transform cursor-grab active:cursor-grabbing"
          >
            <MessageSquare className="w-6 h-6" />
            {/* Animated presence dot */}
            <span className="absolute bottom-1 right-1 w-3 h-3 rounded-full bg-emerald-500 border-2 border-background">
              <motion.span
                className="absolute inset-0 rounded-full bg-emerald-500"
                animate={{ scale: [1, 1.6, 1], opacity: [1, 0, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              />
            </span>
          </motion.button>
        ) : (
          /* ── Open: 380×520 chat panel ── */
          <motion.div
            key="open"
            initial={{ scale: 0.9, opacity: 0, y: 8 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.9, opacity: 0, y: 8 }}
            transition={{ duration: 0.2 }}
            className="w-[380px] h-[520px] rounded-2xl shadow-2xl border border-border bg-card flex flex-col overflow-hidden cursor-grab active:cursor-grabbing"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-2.5 border-b border-border shrink-0">
              <span className="text-sm font-semibold text-foreground">Ask Peblet</span>
              <button
                ref={closeBtnRef}
                type="button"
                onClick={() => {
                  setOpen(false);
                  openRef.current = false;
                }}
                aria-label="Close Peblet"
                className="p-1 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            {/* PebbleChat — stopPropagation so clicks inside don't
                trigger the drag handler above. */}
            <div
              className="flex-1 min-h-0 cursor-auto"
              onMouseDown={(e) => e.stopPropagation()}
            >
              <PebbleChat greeting={greeting} projectContext={projectContext} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>,
    document.body,
  );
}
