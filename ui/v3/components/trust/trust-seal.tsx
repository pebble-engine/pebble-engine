"use client";

/**
 * TrustSeal — Phase 52 (2026-05-22), revised 52b (2026-05-22 night).
 *
 * v1 of this seal mimicked third-party audit marks too closely — NLM
 * adversarial pass flagged it as a "fake notary trap" with real FTC
 * deceptive-marketing exposure. The original used:
 *   - Word "Charter" (authoritative, implies institutional)
 *   - Reference ID "PEB-TC-2026-05-22" (reads like cert number)
 *   - Double border + ornamental star (mimics ISO/SOC 2 layout)
 *   - "Self-attested" buried at small size below the cert ID
 *
 * v2 removes the visual mimicry while keeping the spirit: a Pebble-
 * branded commitment block that uses the brand wordmark as the signing
 * mark, with "Self-attested" promoted to the most prominent line and
 * all faux-cert decoration stripped. Links to /trust for the receipts.
 *
 * The standard self-attestation posture (Linear / Cal.com / Resend /
 * Plausible pre-SOC2) is still the right one — we just have to look
 * like ourselves, not like an auditor.
 */

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { RotatingPebbleLogo } from "@/components/hero/rotating-pebble-logo";

// Effective date is the date this commitment was published.
// Update when the underlying commitments change materially.
const COMMITMENT_EFFECTIVE = "May 22, 2026";

export function TrustSeal({
  shimmerStyle,
}: {
  shimmerStyle: React.CSSProperties;
}) {
  return (
    <Link
      href="/trust"
      aria-label="Read the Pebble Trust Commitment"
      className="block group"
    >
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-80px" }}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
        whileHover={{ y: -2 }}
        className="relative w-full max-w-md mx-auto"
      >
        {/* Single subtle border + soft shadow. NO double border — that's
            the cert-mimicry NLM flagged. This reads as a card, not a
            stamp. */}
        <div className="rounded-2xl bg-card border border-border shadow-[0_8px_30px_rgba(31,29,26,0.06)] px-8 py-9 sm:px-10 sm:py-10 flex flex-col items-center text-center gap-5">

          {/* Headline — "Self-attested" is the LARGEST first thing the
              eye lands on. No "Charter" word, no formal cert language. */}
          <div>
            <p className="text-[11px] font-bold uppercase tracking-[0.25em] text-muted-foreground mb-2">
              Self-attested commitment
            </p>
            <h2 className="text-xl sm:text-2xl font-semibold text-foreground">
              How we handle your data
            </h2>
          </div>

          {/* CENTERPIECE — the rotating Pebble wordmark. The brand IS the
              signature, the way a CEO signs a public commitment. Not the
              way an auditor stamps a certificate. */}
          <div className="py-2">
            <RotatingPebbleLogo
              shimmerStyle={shimmerStyle}
              className="text-3xl sm:text-4xl"
            />
          </div>

          {/* Commitment chips — the three areas this commitment covers. */}
          <div className="flex flex-wrap items-center justify-center gap-2">
            <span className="text-[10px] sm:text-[11px] font-bold uppercase tracking-[0.2em] text-foreground/80 px-2.5 py-1 rounded-full bg-muted">
              GDPR
            </span>
            <span className="text-[10px] sm:text-[11px] font-bold uppercase tracking-[0.2em] text-foreground/80 px-2.5 py-1 rounded-full bg-muted">
              Data Rights
            </span>
            <span className="text-[10px] sm:text-[11px] font-bold uppercase tracking-[0.2em] text-foreground/80 px-2.5 py-1 rounded-full bg-muted">
              Security
            </span>
          </div>

          {/* Effective date — short single line. No cert ID (that was the
              biggest "fake notary" tell). No formal closing block. */}
          <p className="text-xs text-muted-foreground">
            Effective {COMMITMENT_EFFECTIVE} · Pebble Engine
          </p>

          {/* Call-to-receipts — every claim is backed at /trust. */}
          <div className="inline-flex items-center gap-1.5 text-sm font-semibold text-foreground/70 group-hover:text-foreground transition-colors pt-1">
            See what we actually do
            <span aria-hidden className="transition-transform group-hover:translate-x-0.5">→</span>
          </div>
        </div>
      </motion.div>
    </Link>
  );
}
