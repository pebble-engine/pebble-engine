"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesGridClean() {
  return (
    <section className="bg-slate-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="mb-16">
          <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-4" data-pebble-id="pb-ca07eb">
            What we handle
          </p>
          <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight max-w-xl tracking-tight" data-pebble-id="pb-34e30b">
            <RevealWords>Bookkeeping and tax work for businesses that can't afford surprises.</RevealWords>
          </h2>
        </div>

        {/* Services grid — 3 columns, text-only cards */}
        <Stagger className="grid grid-cols-1 md:grid-cols-3 gap-px bg-slate-200">
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-4e162b">
              Small Business Bookkeeping
            </h3>
            <p className="text-slate-500 text-base leading-relaxed flex-1" data-pebble-id="pb-829f26">
              Monthly reconciliation, categorization, and clean books delivered on schedule — so you always know where you stand without digging through spreadsheets.
            </p>
            <a
              href="#contact"
              className="text-sky-600 text-sm font-medium tracking-wide hover:text-sky-700 transition mt-2" data-pebble-id="pb-df6c12">
              Learn more &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-c69143">
              Business Tax Returns
            </h3>
            <p className="text-slate-500 text-base leading-relaxed flex-1" data-pebble-id="pb-5b218d">
              Annual federal and state filings for sole proprietors, LLCs, S-corps, and partnerships. We find deductions others miss and file accurately, on time.
            </p>
            <a
              href="#contact"
              className="text-sky-600 text-sm font-medium tracking-wide hover:text-sky-700 transition mt-2" data-pebble-id="pb-24d913">
              Learn more &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-5fd931">
              Individual Tax Returns
            </h3>
            <p className="text-slate-500 text-base leading-relaxed flex-1" data-pebble-id="pb-c2dddf">
              Straightforward personal returns done right. Whether you have W-2s, freelance income, or rental property, we work through it carefully and explain every line.
            </p>
            <a
              href="#contact"
              className="text-sky-600 text-sm font-medium tracking-wide hover:text-sky-700 transition mt-2" data-pebble-id="pb-a2e431">
              Learn more &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-145060">
              IRS Correspondence & Notices
            </h3>
            <p className="text-slate-500 text-base leading-relaxed flex-1" data-pebble-id="pb-1624fb">
              Got a letter from the IRS? Don't panic. We read it, respond on your behalf, and keep you informed at every step until it's resolved.
            </p>
            <a
              href="#contact"
              className="text-sky-600 text-sm font-medium tracking-wide hover:text-sky-700 transition mt-2" data-pebble-id="pb-8b43c1">
              Learn more &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-f34428">
              Catch-Up Bookkeeping
            </h3>
            <p className="text-slate-500 text-base leading-relaxed flex-1" data-pebble-id="pb-3f33cc">
              Months behind on your books? We sort through the backlog, reconcile the gaps, and get your records current so you can move forward clean.
            </p>
            <a
              href="#contact"
              className="text-sky-600 text-sm font-medium tracking-wide hover:text-sky-700 transition mt-2" data-pebble-id="pb-c83e13">
              Learn more &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-c87d68">
              Free Shoebox Review
            </h3>
            <p className="text-slate-500 text-base leading-relaxed flex-1" data-pebble-id="pb-28b333">
              Bring in your messiest pile of receipts and records. We'll tell you straight what shape your finances are in — no charge, no commitment required.
            </p>
            <a
              href="#contact"
              className="text-sky-600 text-sm font-medium tracking-wide hover:text-sky-700 transition mt-2" data-pebble-id="pb-7534f7">
              Learn more &rarr;
            </a>
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
