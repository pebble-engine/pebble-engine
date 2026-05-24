"use client";

/**
 * ControlCenter — split-pane shell for the Pebble app (2026-05-23).
 *
 * Marc's design-night pivot. The dashboard becomes a two-column shell:
 *   - LEFT  (~480px): PebbleChat — the assistant the user talks to.
 *   - RIGHT (fills):  the actual route content (project grid, templates,
 *                     integrations, etc.) inside the canvas.
 *
 * The chat persists across pane changes for the lifetime of the
 * dashboard mount. The right canvas swaps to whatever child it's
 * handed — so the same component can host /dashboard, and later wrap
 * /designs, /templates, etc.
 *
 * Mobile (< md): the chat tucks into a slide-up drawer triggered by a
 * floating "Ask Pebble" button. The canvas takes the full viewport so
 * a thumb-driven user isn't squeezed into 200px of preview.
 */

import { useState } from "react";
import { MessageSquare, X } from "lucide-react";
import { PebbleChat } from "@/components/pebble-chat";

export type ControlCenterProps = {
  /** Right-side content — the route the user is currently looking at. */
  children: React.ReactNode;
  /** Opening line spoken by Pebble. Pass per-route copy so the
   *  assistant greets in context ("Welcome back to your dashboard"
   *  vs "Browsing templates? I can help filter"). */
  greeting?: string;
};

export function ControlCenter({ children, greeting }: ControlCenterProps) {
  // Mobile drawer state. Always closed on first render so the user
  // sees the canvas first; they tap the floating button to open chat.
  const [mobileChatOpen, setMobileChatOpen] = useState(false);

  return (
    <div className="flex h-screen-safe w-full overflow-hidden bg-background">
      {/* Desktop chat panel — always visible on md+. The fixed width
          matches Marc's mockup (~500px) and keeps the canvas the
          dominant surface. */}
      <aside className="hidden md:flex md:w-[460px] lg:w-[500px] shrink-0 h-full">
        <PebbleChat greeting={greeting} />
      </aside>

      {/* Right canvas — fills remaining width. Scrolls independently
          of the chat so a long page doesn't push the input off-screen. */}
      <section className="flex-1 h-full overflow-y-auto bg-background">
        {children}
      </section>

      {/* Mobile floating Ask Pebble button. Hidden when the drawer
          is open; the drawer's own close button takes over then. */}
      {!mobileChatOpen && (
        <button
          type="button"
          onClick={() => setMobileChatOpen(true)}
          className="md:hidden fixed bottom-6 right-6 z-40 inline-flex items-center gap-2 px-4 py-3 rounded-full bg-foreground text-background shadow-2xl font-semibold text-sm"
          aria-label="Open Pebble chat"
        >
          <MessageSquare className="w-4 h-4" />
          Ask Pebble
        </button>
      )}

      {/* Mobile slide-up drawer. Covers the bottom 80% of the viewport;
          chat behaves identically to the desktop panel inside it. */}
      {mobileChatOpen && (
        <div
          className="md:hidden fixed inset-0 z-50 flex flex-col bg-black/40"
          onClick={() => setMobileChatOpen(false)}
        >
          <div
            className="mt-auto h-[88vh] bg-card border-t border-border rounded-t-2xl flex flex-col overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              type="button"
              onClick={() => setMobileChatOpen(false)}
              className="self-end m-3 p-1.5 rounded-md text-muted-foreground hover:bg-accent hover:text-foreground"
              aria-label="Close chat"
            >
              <X className="w-4 h-4" />
            </button>
            <div className="flex-1 min-h-0">
              <PebbleChat greeting={greeting} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
