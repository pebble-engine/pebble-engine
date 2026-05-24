"use client";
import { FadeIn } from "@/components/ui/FadeIn";

export default function TermsPage() {
  return (
    <main className="min-h-[100dvh] py-32" style={{ background: "var(--color-bg)" }}>
      <div className="max-w-prose mx-auto px-6">
        <FadeIn delay={0.2} duration={0.9}>
          <h1 className="text-4xl md:text-5xl font-display italic mb-8 text-[var(--color-text-primary)]" style={{ fontFamily: "var(--font-display)" }} data-pebble-id="pb-d72c3b">
            Terms of Service
          </h1>
        </FadeIn>
        
        <FadeIn delay={0.4} duration={0.9}>
          <div className="space-y-6 text-[var(--color-text-secondary)]">
            <p data-pebble-id="pb-f66939">By accessing this site and making purchases, you agree to the following straightforward terms. We believe in clear agreements, not fine print.</p>
            
            <h2 className="text-2xl font-display italic text-[var(--color-text-primary)] mt-8" style={{ fontFamily: "var(--font-display)" }} data-pebble-id="pb-b92ffd">Your Responsibilities</h2>
            <ul className="list-disc pl-5 space-y-2">
              <li data-pebble-id="pb-50c3e5">Provide accurate shipping and contact information at checkout</li>
              <li data-pebble-id="pb-e265eb">Respect staff and fellow customers if visiting in person</li>
              <li data-pebble-id="pb-6395de">Use our contact forms and event registration tools honestly</li>
            </ul>

            <h2 className="text-2xl font-display italic text-[var(--color-text-primary)] mt-8" style={{ fontFamily: "var(--font-display)" }} data-pebble-id="pb-886269">Our Commitments</h2>
            <ul className="list-disc pl-5 space-y-2">
              <li data-pebble-id="pb-cbe71b">Books will be packaged responsibly and shipped within 1–2 business days</li>
              <li data-pebble-id="pb-e20d83">Event listings are accurate as of the publication date; we reserve the right to update schedules</li>
              <li data-pebble-id="pb-220ccb">We will not share your personal information with unrelated third parties</li>
            </ul>

            <h2 className="text-2xl font-display italic text-[var(--color-text-primary)] mt-8" style={{ fontFamily: "var(--font-display)" }} data-pebble-id="pb-1fd276">Limitations & Disputes</h2>
            <p data-pebble-id="pb-5596f5">Our liability is limited to the purchase price of the affected item. If a disagreement arises, we agree to resolve it through good-faith mediation in Multnomah County, Oregon, before pursuing formal legal channels.</p>
          </div>
        </FadeIn>
      </div>
    </main>
  );
}