"use client";

/**
 * TrustSeal — Phase 52 (2026-05-22).
 *
 * The Pebble Trust Charter seal. Marc's call after reviewing the
 * three-card trust row: the cards felt "too I-made-these-up." This
 * replaces them with a single elegant certificate-style seal that
 *
 *   1. Uses the rotating Pebble wordmark as the centerpiece — the
 *      brand IS the attestation mark, like a notary's seal or a
 *      corporate watermark.
 *   2. Is honest about being self-attested (not externally certified)
 *      while showing the underlying evidence: links to /privacy, /dpa,
 *      and the full /trust charter where every claim is backed by a
 *      specific control.
 *   3. Looks like a real document seal (double border, formal type,
 *      effective date, reference ID) — not a sticker, not a fake
 *      ISO/SOC2 trademark.
 *
 * Self-attestation is the standard posture for SaaS at this stage:
 * Linear, Cal.com, Resend, Plausible all do this until their first
 * SOC 2 audit lands. This component matches that pattern.
 */

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { RotatingPebbleLogo } from "@/components/hero/rotating-pebble-logo";

// Effective date is the date this charter was published.
// Update when the underlying charter text materially changes.
const TRUST_CHARTER_EFFECTIVE = "May 22, 2026";

// Reference ID — short stable identifier visible on the seal. Format:
//   PEB-TC-YYYY-MM-DD
// Renders as small print at the bottom. Cosmetic but professional —
// real corporate seals always carry a reference number.
const TRUST_CHARTER_REF = "PEB-TC-2026-05-22";

export function TrustSeal({
  shimmerStyle,
}: {
  shimmerStyle: React.CSSProperties;
}) {
  return (
    <Link
      href="/trust"
      aria-label="Read the Pebble Trust Charter"
      className="block group"
    >
      <motion.div
        initial={{ opacity: 0, y: 12, scale: 0.98 }}
        whileInView={{ opacity: 1, y: 0, scale: 1 }}
        viewport={{ once: true, margin: "-80px" }}
        transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
        whileHover={{ y: -2 }}
        className="relative w-full max-w-md mx-auto"
      >
        {/* Outer + inner border = formal double-line "this is a document"
            visual. Subtle so it doesn't fight the brand mark inside. */}
        <div className="rounded-2xl bg-card border border-foreground/15 shadow-[0_12px_40px_rgba(31,29,26,0.08)] p-1.5">
          <div className="rounded-xl border border-foreground/10 px-8 py-9 sm:px-12 sm:py-10 flex flex-col items-center text-center gap-4">

            {/* Eyebrow — what this seal is, formally */}
            <p className="text-[10px] sm:text-[11px] font-bold uppercase tracking-[0.3em] text-muted-foreground">
              Pebble Trust Charter
            </p>

            {/* Ornamental rule — pure typography flourish, like the
                pinstripe above/below an "Of the United States" on
                official documents. */}
            <div className="flex items-center gap-2 text-muted-foreground/40">
              <span className="h-px w-12 bg-current" />
              <span className="text-[10px]">✦</span>
              <span className="h-px w-12 bg-current" />
            </div>

            {/* CENTERPIECE — rotating Pebble wordmark. The mark IS the
                seal. ~3rem on desktop, 2.25rem on mobile so it visually
                anchors the certificate. */}
            <div className="my-1">
              <RotatingPebbleLogo
                shimmerStyle={shimmerStyle}
                className="text-4xl sm:text-5xl"
              />
            </div>

            {/* Commitment chips — the three areas this charter covers.
                Visual rhythm matching the eyebrow's spaced-caps style. */}
            <div className="flex flex-wrap items-center justify-center gap-2 mt-2">
              <span className="text-[10px] sm:text-[11px] font-bold uppercase tracking-[0.2em] text-foreground/80 px-2.5 py-1 rounded-full border border-foreground/15">
                GDPR
              </span>
              <span className="text-[10px] sm:text-[11px] font-bold uppercase tracking-[0.2em] text-foreground/80 px-2.5 py-1 rounded-full border border-foreground/15">
                Data Rights
              </span>
              <span className="text-[10px] sm:text-[11px] font-bold uppercase tracking-[0.2em] text-foreground/80 px-2.5 py-1 rounded-full border border-foreground/15">
                Security
              </span>
            </div>

            {/* Signature / effective date block — formal cert closer.
                Mirrors the layout of a real notary or corporate seal. */}
            <div className="mt-4 space-y-1">
              <p className="text-[10px] font-bold uppercase tracking-[0.25em] text-muted-foreground">
                Effective {TRUST_CHARTER_EFFECTIVE}
              </p>
              <p className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground/70">
                Self-attested by Pebble Engine
              </p>
              <p className="font-mono text-[9px] text-muted-foreground/50 pt-1">
                {TRUST_CHARTER_REF}
              </p>
            </div>

            {/* Call-to-charter — discreet, lets visitors who want the
                receipts click through to the full document. */}
            <div className="mt-3 inline-flex items-center gap-1.5 text-xs font-semibold text-foreground/70 group-hover:text-foreground transition-colors">
              Read the charter
              <span aria-hidden className="transition-transform group-hover:translate-x-0.5">→</span>
            </div>
          </div>
        </div>
      </motion.div>
    </Link>
  );
}
