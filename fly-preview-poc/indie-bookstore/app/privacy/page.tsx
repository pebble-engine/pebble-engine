"use client";
import { FadeIn } from "@/components/ui/FadeIn";

export default function PrivacyPage() {
  return (
    <main className="min-h-[100dvh] py-32" style={{ background: "var(--color-bg)" }}>
      <div className="max-w-prose mx-auto px-6">
        <FadeIn delay={0.2} duration={0.9}>
          <h1 className="text-4xl md:text-5xl font-display italic mb-8 text-[var(--color-text-primary)]" style={{ fontFamily: "var(--font-display)" }} data-pebble-id="pb-230ec4">
            Privacy Policy
          </h1>
        </FadeIn>
        
        <FadeIn delay={0.4} duration={0.9}>
          <div className="space-y-6 text-[var(--color-text-secondary)]">
            <p data-pebble-id="pb-70f267">We collect only what we need to process your orders and communicate about events. We do not sell your data to third-party marketers or algorithmic ad networks.</p>
            
            <h2 className="text-2xl font-display italic text-[var(--color-text-primary)] mt-8" style={{ fontFamily: "var(--font-display)" }} data-pebble-id="pb-1e59c4">Information We Collect</h2>
            <ul className="list-disc pl-5 space-y-2">
              <li data-pebble-id="pb-c58d8a">Name and email address (for order confirmations and event RSVPs)</li>
              <li data-pebble-id="pb-b4ee3f">Shipping address (only when you select delivery)</li>
              <li data-pebble-id="pb-53e5fa">Device information (basic, anonymized analytics to improve site performance)</li>
            </ul>

            <h2 className="text-2xl font-display italic text-[var(--color-text-primary)] mt-8" style={{ fontFamily: "var(--font-display)" }} data-pebble-id="pb-7215c3">How We Use Your Data</h2>
            <p data-pebble-id="pb-b00652">We use your information strictly to fulfill purchases, send receipt updates, and notify you about events you explicitly sign up for. You can opt out of marketing emails at any time using the link in our correspondence.</p>

            <h2 className="text-2xl font-display italic text-[var(--color-text-primary)] mt-8" style={{ fontFamily: "var(--font-display)" }} data-pebble-id="pb-eb04bc">Your Rights</h2>
            <p data-pebble-id="pb-d4b487">You may request a copy of your data, or ask us to delete it entirely, by emailing us at [EMAIL]. We respond within 14 days. We retain purchase records for tax purposes as required by Oregon state law.</p>
          </div>
        </FadeIn>
      </div>
    </main>
  );
}