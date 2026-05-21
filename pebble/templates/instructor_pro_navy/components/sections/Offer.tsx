"use client";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/Button";
import { OFFER_HEADING, OFFER_BODY, OFFER_CTA } from "@/content/site";

/**
 * Centered glass offer card on a red shimmer-band gradient backdrop per
 * DNA notes. Shield icon + heading + paragraph + email CTA.
 */
export function Offer() {
  return (
    <section className="relative py-16 sm:py-20">
      <div className="mx-auto max-w-5xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 18 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="shimmer-band relative overflow-hidden rounded-3xl border border-accent/30 bg-gradient-to-br from-accent/15 via-card to-card p-8 sm:p-12"
        >
          <div className="flex flex-col items-center gap-5 text-center">
            <span className="inline-flex h-14 w-14 items-center justify-center rounded-2xl border border-accent/40 bg-accent/15 text-accent">
              <ShieldIcon />
            </span>
            <h3 className="font-display text-3xl font-black uppercase tracking-headline text-fg sm:text-4xl">
              {OFFER_HEADING}
            </h3>
            <p className="max-w-2xl text-base text-body">{OFFER_BODY}</p>
            <Button href="/contact" size="lg" variant="gold">
              {OFFER_CTA}
            </Button>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

function ShieldIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      <path d="m9 12 2 2 4-4" />
    </svg>
  );
}
