"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { getBrandKit, saveBrandKit, type BrandKit } from "@/lib/api";

// Engine-safe accent fonts (all in next/font/google).
const FONTS = ["", "Inter", "Playfair Display", "DM Sans", "Lato", "Space Grotesk", "Merriweather", "JetBrains Mono"];

/**
 * P3 — "My brand kit": account-wide colors / font / voice that every new
 * build inherits. Autosaves like the knowledge card.
 */
export function BrandKitCard() {
  const [kit, setKit] = useState<BrandKit>({});
  const [status, setStatus] = useState<"loading" | "idle" | "saving" | "saved" | "error">("loading");
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    let alive = true;
    getBrandKit()
      .then((r) => { if (alive) { setKit(r.brand_kit || {}); setStatus("idle"); } })
      .catch(() => { if (alive) setStatus("error"); });
    return () => { alive = false; };
  }, []);

  const persist = useCallback(async (next: BrandKit) => {
    setStatus("saving");
    try { await saveBrandKit(next); setStatus("saved"); }
    catch { setStatus("error"); }
  }, []);

  const update = (patch: Partial<BrandKit>) => {
    const next = { ...kit, ...patch };
    setKit(next);
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => persist(next), 700);
  };

  const statusLabel =
    status === "loading" ? "Loading…"
    : status === "saving" ? "Saving…"
    : status === "saved" ? "Saved ✓"
    : status === "error" ? "Couldn't save" : "";

  return (
    <section className="rounded-2xl border border-border bg-card p-5 sm:p-6">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-foreground">My brand kit</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Colors, font, and voice every new site inherits — set your brand once.
          </p>
        </div>
        <span className={`shrink-0 text-xs ${status === "error" ? "text-destructive" : "text-muted-foreground"}`} aria-live="polite">
          {statusLabel}
        </span>
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <label className="flex items-center gap-3 text-sm text-foreground">
          <input type="color" aria-label="Primary brand color"
            value={kit.primary_color || "#1f6feb"}
            onChange={(e) => update({ primary_color: e.target.value })}
            className="h-9 w-12 rounded-md border border-border bg-background p-0.5" />
          Primary color
        </label>
        <label className="flex items-center gap-3 text-sm text-foreground">
          <input type="color" aria-label="Accent color"
            value={kit.accent_color || "#f59e0b"}
            onChange={(e) => update({ accent_color: e.target.value })}
            className="h-9 w-12 rounded-md border border-border bg-background p-0.5" />
          Accent color
        </label>
        <label className="flex flex-col gap-1 text-sm text-foreground">
          Display font
          <select
            aria-label="Display font"
            value={kit.font || ""}
            onChange={(e) => update({ font: e.target.value })}
            className="rounded-xl border border-border bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            {FONTS.map((f) => <option key={f || "default"} value={f}>{f || "Default (Inter)"}</option>)}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm text-foreground">
          Brand voice
          <input
            type="text"
            aria-label="Brand voice"
            value={kit.voice || ""}
            onChange={(e) => update({ voice: e.target.value })}
            placeholder="e.g. warm and plain-spoken"
            className="rounded-xl border border-border bg-background px-3 py-2 text-sm placeholder:text-muted-foreground/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
        </label>
      </div>
    </section>
  );
}
