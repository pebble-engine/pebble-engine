"use client";

/**
 * ControlCenter — three-pane shell for the Pebble app (2026-05-23 rev 2).
 *
 * Marc's updated mockup put the chat panel on the RIGHT (narrower,
 * ~340px) and kept the existing DashboardSidebar on the LEFT. The
 * canvas takes the middle. So the shell is:
 *
 *   [ DashboardSidebar (240px) ] [ canvas (flex-1) ] [ PebbleChat (340px) ]
 *
 * The left sidebar is a slot so other routes can supply their own
 * sidebar (or none) without rewriting the shell. The right chat
 * panel is owned here — it's the always-present assistant surface
 * Marc wants users to trust as the catch-all "find anything" lane.
 *
 * Mobile (< lg):
 *   - Sidebar collapses behind a drawer (existing DashboardSidebar
 *     behavior — it shrinks to a hamburger).
 *   - Chat panel tucks into a slide-up sheet triggered by a floating
 *     "Ask Peblet" pill that sits over the canvas.
 *   - Canvas is full-width so the user isn't squeezed into 200px.
 */

import { useState } from "react";
import { MessageSquare, X, ChevronLeft } from "lucide-react";
import { PebbleChat } from "@/components/pebble-chat";
import { type ChatProjectContext } from "@/lib/api";

export type ControlCenterProps = {
  /** Middle column — the actual route content the user is looking at. */
  children: React.ReactNode;
  /** Optional left sidebar. Most authed routes pass a DashboardSidebar
   *  here; some pages (workspace shell) want to omit. */
  leftSidebar?: React.ReactNode;
  /** Opening line spoken by Peblet on mount. Per-route copy lets the
   *  greeting feel context-aware ("Welcome back to your dashboard" vs
   *  "Browsing templates? I can help filter"). */
  greeting?: string;
  /** Optional project context passed from pages that load project data.
   *  Enables Pebble chat to give project-aware replies and dispatch edits. */
  projectContext?: ChatProjectContext | null;
};

export function ControlCenter({ children, leftSidebar, greeting, projectContext }: ControlCenterProps) {
  const [mobileChatOpen, setMobileChatOpen] = useState(false);
  const [chatCollapsed, setChatCollapsed] = useState(false);

  return (
    <div className="flex h-full w-full overflow-hidden bg-background">
      {/* LEFT — workspace sidebar. Hidden under lg; the existing
          DashboardSidebar handles its own mobile drawer pattern. */}
      {leftSidebar && (
        <aside className="hidden lg:flex shrink-0 h-full">
          {leftSidebar}
        </aside>
      )}

      {/* MIDDLE — canvas. Scrolls independently so a long page
          doesn't push the chat input off-screen. */}
      <section className="flex-1 h-full overflow-y-auto bg-background min-w-0">
        {children}
      </section>

      {/* RIGHT — chat panel on desktop. Collapses to a 48px strip
          so users can reclaim canvas space without fully dismissing
          the assistant. Expand/collapse via chevron buttons. */}
      {chatCollapsed ? (
        <aside className="hidden lg:flex lg:flex-col w-12 shrink-0 h-full border-l border-border bg-card items-center pt-3 gap-2">
          <button
            type="button"
            onClick={() => setChatCollapsed(false)}
            className="p-1.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
            aria-label="Open Pebble chat"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span
            style={{ writingMode: "vertical-rl", transform: "rotate(180deg)" }}
            className="text-[10px] font-semibold text-muted-foreground/50 tracking-widest mt-1 select-none"
          >
            Ask Pebble
          </span>
        </aside>
      ) : (
        <aside className="hidden lg:flex lg:w-[340px] xl:w-[360px] shrink-0 h-full">
          <PebbleChat greeting={greeting} onCollapse={() => setChatCollapsed(true)} projectContext={projectContext} />
        </aside>
      )}

      {/* Mobile floating "Ask Peblet" pill — opens the chat sheet. */}
      {!mobileChatOpen && (
        <button
          type="button"
          onClick={() => setMobileChatOpen(true)}
          className="lg:hidden fixed bottom-6 right-6 z-40 inline-flex items-center gap-2 px-4 py-3 rounded-full bg-foreground text-background shadow-2xl font-semibold text-sm"
          aria-label="Open Peblet chat"
        >
          <MessageSquare className="w-4 h-4" />
          Ask Peblet
        </button>
      )}

      {/* Mobile slide-up sheet — chat behaves identically inside. */}
      {mobileChatOpen && (
        <div
          className="lg:hidden fixed inset-0 z-50 flex flex-col bg-black/40"
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
              <PebbleChat greeting={greeting} projectContext={projectContext} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
