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
import { Droplet } from "lucide-react";

// Effective date is the date this commitment was published.
// Update when the underlying commitments change materially.
const COMMITMENT_EFFECTIVE = "May 22, 2026";

// Phase 53 (2026-05-23): the seal had the rotating Pebble wordmark as
// the centerpiece, but the same wordmark also dominates §7 (final CTA)
// — two rotating wordmarks on the same page reads as redundant. Marc's
// call: strip from both. The seal's centerpiece is now the Pebble
// droplet (the brand mark already used in the publish-phase ripple +
// dashboard nav) — branded, but visually quieter than the wordmark, so
// the SELF-ATTESTED COMMITMENT framing carries the meaning. The
// shimmerStyle prop is preserved on the component signature for API
// stability even though we no longer use the rotating wordmark here.

export function TrustSeal({
  shimmerStyle: _shimmerStyle,
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

          {/* CENTERPIECE — Pebble droplet, the brand mark. Quieter than
              the rotating wordmark which lives elsewhere on the page;
              the "SELF-ATTESTED COMMITMENT" eyebrow carries the
              certification framing. */}
          <div className="py-2 text-foreground">
            <Droplet
              className="w-12 h-12 sm:w-14 sm:h-14 fill-current"
              strokeWidth={1.5}
              aria-hidden
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
