"use client";

/**
 * Brand marks — minimal SVG glyphs for each integration vendor.
 *
 * Marc's 2026-05-23 brief: "put the company's color and the company's
 * logo in the background of the actual card." McDonald's red/gold,
 * Taco Bell purple, etc.
 *
 * Why hand-rolled SVGs rather than a brand-icons package:
 *   - No new npm dependency for a tiny set (10 marks).
 *   - Full control over color (each glyph paints with currentColor
 *     so a single component handles light/dark + brand-color
 *     backgrounds without a second copy).
 *   - We avoid the IP grey-zone of redistributing an icon pack — these
 *     are minimal evocative shapes (a letter mark, a stripe, a square),
 *     not pixel-perfect company logos. "Recognizable enough to feel
 *     branded, abstract enough that no trademark conversation starts."
 *
 * Each mark is a 24×24 viewBox SVG with `fill="currentColor"` so the
 * caller controls color via Tailwind's `text-*` class.
 */

import React from "react";

type MarkProps = { className?: string };

// ── Stripe — purple, "S" stripe mark ─────────────────────────── //
export function StripeMark({ className = "" }: MarkProps) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="currentColor" aria-hidden>
      <path d="M13.5 9.6c0-.8.7-1.1 1.8-1.1 1.6 0 3.7.5 5.3 1.4V5.1c-1.8-.7-3.5-1-5.3-1-4.3 0-7.2 2.3-7.2 6.1 0 5.9 8.2 5 8.2 7.5 0 1-.9 1.3-2 1.3-1.8 0-4.1-.7-5.9-1.7v4.8c2 .9 4 1.2 5.9 1.2 4.4 0 7.5-2.2 7.5-6.1-.1-6.3-8.3-5.3-8.3-7.6z"/>
    </svg>
  );
}

// ── Resend — black, simple square monogram ───────────────────── //
export function ResendMark({ className = "" }: MarkProps) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="currentColor" aria-hidden>
      <path d="M3 3h18v18H3V3zm5 4v10h2.6v-3.3h.5l2.6 3.3H17l-3.2-3.9c1.3-.5 2.1-1.6 2.1-3.1C15.9 8.2 14.4 7 12.1 7H8zm2.6 1.9h1.4c1 0 1.6.5 1.6 1.4 0 1-.6 1.5-1.6 1.5h-1.4V8.9z"/>
    </svg>
  );
}

// ── Mailchimp — banana yellow, the cap ───────────────────────── //
export function MailchimpMark({ className = "" }: MarkProps) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="currentColor" aria-hidden>
      <path d="M17.2 14.5c-.2 0-.4 0-.6.1.1-.5.1-1 0-1.5.3-2.1-.4-3.8-1.7-4.5-.8-.4-1.7-.4-2.6 0L11 9.3 9.5 7.7c-.5-.6-1.3-.8-1.9-.4-1.4 1-1.8 3.2-.8 5.2-2.3 2.1-3.6 4.4-3.1 6.3.7 2.5 4.6 3.9 9 3.2 4.4-.7 7.4-3.5 6.7-6.1-.3-.8-1.2-1.4-2.2-1.4zm-9.3 4.7c-1.3.2-2.6-.6-2.9-1.7-.3-1.1.5-2.2 1.8-2.5 1.3-.2 2.6.6 2.9 1.7.3 1.1-.5 2.2-1.8 2.5z"/>
    </svg>
  );
}

// ── Plausible — indigo, the simple wave ──────────────────────── //
export function PlausibleMark({ className = "" }: MarkProps) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="currentColor" aria-hidden>
      <path d="M3 17h2.5L8 8l3 12 3-16 3 13 2-7h2v2h-1l-2.5 9-3-13-3 16-3-12-1.5 5H3v-2z"/>
    </svg>
  );
}

// ── Google Analytics — orange + yellow, the bar shape ────────── //
export function GoogleAnalyticsMark({ className = "" }: MarkProps) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="currentColor" aria-hidden>
      <path d="M14.5 3c-1.4 0-2.5 1.1-2.5 2.5v13c0 1.4 1.1 2.5 2.5 2.5S17 19.9 17 18.5v-13C17 4.1 15.9 3 14.5 3zM4.5 16c-1.4 0-2.5 1.1-2.5 2.5S3.1 21 4.5 21 7 19.9 7 18.5 5.9 16 4.5 16zm5-7C8.1 9 7 10.1 7 11.5v7c0 1.4 1.1 2.5 2.5 2.5s2.5-1.1 2.5-2.5v-7C12 10.1 10.9 9 9.5 9z"/>
    </svg>
  );
}

// ── Calendly — Calendly blue, calendar with dot ──────────────── //
export function CalendlyMark({ className = "" }: MarkProps) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="currentColor" aria-hidden>
      <path d="M19 4h-2V2h-2v2H9V2H7v2H5C3.9 4 3 4.9 3 6v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10zm0-12H5V6h14v2zm-9 6c0 1.1.9 2 2 2s2-.9 2-2-.9-2-2-2-2 .9-2 2z"/>
    </svg>
  );
}

// ── Slack — multicolor aubergine, the hash motif ─────────────── //
export function SlackMark({ className = "" }: MarkProps) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="currentColor" aria-hidden>
      <path d="M5.4 14.7c0 1-.8 1.9-1.9 1.9-1 0-1.9-.8-1.9-1.9 0-1 .8-1.9 1.9-1.9h1.9v1.9zm.9 0c0-1 .8-1.9 1.9-1.9 1 0 1.9.8 1.9 1.9v4.6c0 1-.8 1.9-1.9 1.9-1 0-1.9-.8-1.9-1.9v-4.6zm1.9-7.4c-1 0-1.9-.8-1.9-1.9s.8-1.9 1.9-1.9 1.9.8 1.9 1.9v1.9H8.2zm0 .9c1 0 1.9.8 1.9 1.9 0 1-.8 1.9-1.9 1.9H3.6c-1 0-1.9-.8-1.9-1.9 0-1 .8-1.9 1.9-1.9h4.6zm7.4 1.9c0-1 .8-1.9 1.9-1.9 1 0 1.9.8 1.9 1.9 0 1-.8 1.9-1.9 1.9h-1.9V10.1zm-.9 0c0 1-.8 1.9-1.9 1.9-1 0-1.9-.8-1.9-1.9V5.4c0-1 .8-1.9 1.9-1.9 1 0 1.9.8 1.9 1.9v4.7zm-1.9 7.4c1 0 1.9.8 1.9 1.9 0 1-.8 1.9-1.9 1.9-1 0-1.9-.8-1.9-1.9v-1.9h1.9zm0-.9c-1 0-1.9-.8-1.9-1.9 0-1 .8-1.9 1.9-1.9h4.7c1 0 1.9.8 1.9 1.9 0 1-.8 1.9-1.9 1.9h-4.7z"/>
    </svg>
  );
}

// ── Supabase — green wave ────────────────────────────────────── //
export function SupabaseMark({ className = "" }: MarkProps) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="currentColor" aria-hidden>
      <path d="M13.3 22.9c-.6.8-1.9.4-2-.6l-.5-7.6h6.4c1.2 0 1.8 1.4 1.1 2.3l-5 5.9zm-2.6-21.8c.6-.8 1.9-.4 2 .6l.5 7.6H6.8c-1.2 0-1.8-1.4-1.1-2.3l5-5.9z"/>
    </svg>
  );
}

// ── Zapier — orange Z-bolt ───────────────────────────────────── //
export function ZapierMark({ className = "" }: MarkProps) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="currentColor" aria-hidden>
      <path d="M14 2L4 14h6l-2 8 10-12h-6l2-8z"/>
    </svg>
  );
}

// ── Custom webhook — Pebble blue, terminal/code-y ────────────── //
export function WebhookMark({ className = "" }: MarkProps) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="currentColor" aria-hidden>
      <path d="M10 14.4l-2.4 2.4-1.4-1.4 2.4-2.4-2.4-2.4 1.4-1.4 2.4 2.4 2.4-2.4 1.4 1.4-2.4 2.4 2.4 2.4-1.4 1.4L10 14.4zm6-9.4c1.7 0 3 1.3 3 3v12c0 1.7-1.3 3-3 3H8c-1.7 0-3-1.3-3-3V8c0-1.7 1.3-3 3-3h2V3h2v2h2V3h2v2zm0 2h-8v12h8V7z"/>
    </svg>
  );
}

// ── Mark registry — one source of truth for {color, mark, accent} //
//
// The COLOR is the deep brand color we paint in the card background
// (deep enough that white text reads). The MARK is the glyph drawn
// on the right side at low opacity. The ACCENT is a lighter shade
// used for hover-state highlights.

export type BrandIdentity = {
  /** Hex background for the colored swatch portion of the card. */
  bg:     string;
  /** Hex for hover / accent shade. */
  accent: string;
  /** Glyph component. */
  Mark:   React.FC<MarkProps>;
};

export const BRAND_IDENTITY: Record<string, BrandIdentity> = {
  "Stripe Payments":     { bg: "#635BFF", accent: "#7A73FF", Mark: StripeMark           },
  "Resend":              { bg: "#000000", accent: "#1A1A1A", Mark: ResendMark           },
  "Mailchimp":           { bg: "#FFE01B", accent: "#FFD600", Mark: MailchimpMark        },
  "Plausible Analytics": { bg: "#5850EC", accent: "#6F67F0", Mark: PlausibleMark        },
  "Google Analytics":    { bg: "#F9AB00", accent: "#FFBE2B", Mark: GoogleAnalyticsMark  },
  "Calendly":            { bg: "#006BFF", accent: "#1F7FFF", Mark: CalendlyMark         },
  "Slack":               { bg: "#4A154B", accent: "#5E1A5F", Mark: SlackMark            },
  "Supabase":            { bg: "#3ECF8E", accent: "#5BD89F", Mark: SupabaseMark         },
  "Zapier":              { bg: "#FF4F00", accent: "#FF6A2B", Mark: ZapierMark           },
  "Custom webhook":      { bg: "#3054ff", accent: "#5070FF", Mark: WebhookMark          },
};
