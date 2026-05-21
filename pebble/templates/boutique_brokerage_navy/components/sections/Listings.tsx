"use client";

import * as React from "react";
import { motion, useReducedMotion } from "framer-motion";
import { Button } from "@/components/ui/Button";
import { PropertyCard } from "@/components/ui/PropertyCard";
import { SectionDivider } from "@/components/ui/SectionDivider";
import {
  LISTINGS_EYEBROW,
  LISTINGS_HEADLINE_LINE_1,
  LISTINGS_HEADLINE_LINE_2,
  LISTINGS_CTA,
  LISTINGS_CTA_HREF,
  LISTINGS,
} from "@/content/site";

/**
 * Listings — three-column aspect-4/5 property card grid. The headline +
 * outline CTA sit on the same row at desktop. When LISTINGS is empty
 * (anti-slop default — never invent inventory), the grid is replaced by
 * a quiet placeholder that points to the contact form.
 */
export function Listings() {
  const reduce = useReducedMotion();
  const hasListings = LISTINGS.length > 0;

  return (
    <section
      id="listings"
      aria-labelledby="listings-heading"
      className="bg-bg"
    >
      <div className="page-container">
        <SectionDivider index="02" label="Inventory" />
      </div>

      <div className="page-container pb-section-mobile md:pb-section-desktop">
        {/* Header row */}
        <div className="mb-12 md:mb-16 flex flex-col md:flex-row md:items-end md:justify-between gap-6">
          <div className="max-w-2xl">
            <p className="text-label mb-4">{LISTINGS_EYEBROW}</p>
            <h2 id="listings-heading" className="text-headline">
              {LISTINGS_HEADLINE_LINE_1}
              <br />
              <span className="text-accent">{LISTINGS_HEADLINE_LINE_2}</span>
            </h2>
          </div>
          <Button href={LISTINGS_CTA_HREF} variant="outline">
            {LISTINGS_CTA}
          </Button>
        </div>

        {hasListings ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 md:gap-6">
            {LISTINGS.map((listing, i) => (
              <motion.div
                key={listing.id}
                initial={{ opacity: 0, y: reduce ? 0 : 32 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-80px" }}
                transition={{
                  duration: 0.8,
                  delay: i * 0.15,
                  ease: [0.16, 1, 0.3, 1],
                }}
              >
                <PropertyCard
                  name={listing.name}
                  location={listing.location}
                  beds={listing.beds}
                  baths={listing.baths}
                  price={listing.price}
                  imageUrl={listing.image_url}
                  href={listing.href}
                  badge={listing.badge}
                />
              </motion.div>
            ))}
          </div>
        ) : (
          /* Honest placeholder — no invented listings. */
          <div className="border border-border cinematic-radius p-10 md:p-16 text-center">
            <p className="text-eyebrow mb-4">Inventory is by introduction</p>
            <p className="text-body-lg max-w-xl mx-auto mb-8">
              Active properties are not published. To see what we currently
              represent on the shoreline, request a private introduction.
            </p>
            <Button href="/contact" variant="cinematic">
              Request an Introduction
            </Button>
          </div>
        )}
      </div>
    </section>
  );
}
