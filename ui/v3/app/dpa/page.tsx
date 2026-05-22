import Link from "next/link";
import { MarketingShell, MarketingProse } from "@/components/marketing-shell";

/**
 * /dpa — Phase 47 (2026-05-22).
 *
 * Honest "Data Processing Addendum available on request" page. We don't
 * publish the contract itself (terms vary by customer + jurisdiction)
 * but we DO publish:
 *   - the canonical list of sub-processors,
 *   - a summary of what the DPA covers,
 *   - a contact mechanism to request the signed contract.
 *
 * This is the same posture every B2B SaaS at our stage takes — Stripe,
 * Vercel, Linear all do this for sub-$1M ARR customers. Self-serve DPA
 * portals come later, after the auditor calls them necessary.
 */

const EFFECTIVE_DATE = "May 22, 2026";

const SUB_PROCESSORS = [
  { name: "Supabase",   purpose: "Authentication + Postgres database + file storage", region: "United States",  url: "https://supabase.com/privacy" },
  { name: "Stripe",     purpose: "Subscription billing + payment processing",         region: "United States",  url: "https://stripe.com/privacy" },
  { name: "Resend",     purpose: "Transactional email (signup, password reset, form replies)", region: "United States", url: "https://resend.com/legal/privacy-policy" },
  { name: "Cloudflare", purpose: "CDN + DDoS protection + DNS",                       region: "Global edge",    url: "https://www.cloudflare.com/privacypolicy/" },
  { name: "Railway",    purpose: "Application hosting for the Pebble engine",         region: "United States",  url: "https://railway.app/legal/privacy" },
  { name: "Vercel",     purpose: "Hosting for the customer-facing Pebble app",        region: "Global edge",    url: "https://vercel.com/legal/privacy-policy" },
  { name: "Anthropic",  purpose: "LLM provider — generates site code from your brief", region: "United States", url: "https://www.anthropic.com/legal/privacy" },
  { name: "Google",     purpose: "LLM provider (Gemini) — alternate generator",       region: "United States",  url: "https://policies.google.com/privacy" },
  { name: "OpenRouter", purpose: "LLM gateway (Qwen) — alternate generator",          region: "United States",  url: "https://openrouter.ai/privacy" },
];

export default function DPAPage() {
  return (
    <MarketingShell>
      <MarketingProse>
        <h1 className="text-4xl font-semibold tracking-tight text-[#1a1a1a] mb-2">
          Data Processing Addendum
        </h1>
        <p className="text-sm text-[#1a1a1a]/55 mb-12">Effective {EFFECTIVE_DATE}</p>

        <div className="space-y-10 text-base leading-relaxed text-[#1a1a1a]/75">
          <section>
            <h2 className="text-xl font-semibold text-[#1a1a1a] mb-3">
              What this page is
            </h2>
            <p>
              A Data Processing Addendum (DPA) is the contract that governs how
              Pebble handles your personal data on your behalf when you use our
              service. It satisfies the requirements of Article 28 of the GDPR
              and the equivalent provisions of the UK GDPR + the California
              Consumer Privacy Act (CCPA / CPRA).
            </p>
            <p className="mt-3">
              This page is a <strong>summary</strong> of what&apos;s in our DPA — not the
              contract itself. To execute a signed DPA for your account, email{" "}
              <a href="mailto:web@getpebble.net?subject=DPA%20Request" className="underline hover:text-[#1a1a1a] transition-colors">
                web@getpebble.net
              </a>{" "}
              and we&apos;ll send the current version inside one business day.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[#1a1a1a] mb-3">
              What our DPA covers
            </h2>
            <ul className="space-y-3 list-disc pl-6">
              <li><strong>Roles.</strong> You are the data controller. Pebble is the data processor for personal data you upload, type into the questionnaire, or collect through your published site&apos;s forms.</li>
              <li><strong>Scope.</strong> Data we process is limited to what&apos;s needed to deliver the service — account info, questionnaire answers, generated site files, form submissions sent to your inbox.</li>
              <li><strong>Sub-processors.</strong> Listed below. We give 30 days&apos; notice before adding a new sub-processor that processes personal data on your behalf.</li>
              <li><strong>Security.</strong> Encryption in transit (TLS 1.2+), encryption at rest for all sentinel files + database rows, hashed passwords (Supabase / Argon2), per-user storage isolation in our output directory.</li>
              <li><strong>International transfers.</strong> Standard Contractual Clauses (SCCs) for any EEA → US transfer, including transfers to our sub-processors.</li>
              <li><strong>Data subject rights.</strong> We help you respond to access, rectification, erasure, and portability requests within reasonable timelines — the same controls power our own account-deletion flow, which is documented in our <Link href="/privacy" className="underline hover:text-[#1a1a1a] transition-colors">Privacy Policy</Link>.</li>
              <li><strong>Breach notification.</strong> We notify you without undue delay (target: 48 hours) of any confirmed personal-data breach affecting your data.</li>
              <li><strong>Deletion on termination.</strong> When you delete your account, all personal data is purged within the cooling-off window (default 14 days). Sub-processor cleanup runs the same week.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[#1a1a1a] mb-3">
              Sub-processors
            </h2>
            <p className="mb-4">
              These are the third-party services Pebble depends on. Each handles
              a specific slice of your data — none holds the full picture.
            </p>
            <div className="overflow-x-auto -mx-2 sm:mx-0">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="border-b border-[#1a1a1a]/15">
                    <th className="text-left px-3 py-2 font-semibold text-[#1a1a1a]">Sub-processor</th>
                    <th className="text-left px-3 py-2 font-semibold text-[#1a1a1a]">Purpose</th>
                    <th className="text-left px-3 py-2 font-semibold text-[#1a1a1a] hidden sm:table-cell">Region</th>
                  </tr>
                </thead>
                <tbody>
                  {SUB_PROCESSORS.map((p) => (
                    <tr key={p.name} className="border-b border-[#1a1a1a]/10">
                      <td className="px-3 py-3 align-top">
                        <a href={p.url} target="_blank" rel="noopener noreferrer" className="font-medium text-[#1a1a1a] underline hover:no-underline">
                          {p.name}
                        </a>
                      </td>
                      <td className="px-3 py-3 align-top text-[#1a1a1a]/70">{p.purpose}</td>
                      <td className="px-3 py-3 align-top text-[#1a1a1a]/55 hidden sm:table-cell">{p.region}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="mt-4 text-sm">
              We&apos;ll send 30 days&apos; advance notice to your account email
              when adding a new sub-processor that processes your personal
              data. You can object — if we can&apos;t resolve the concern,
              you can cancel without penalty.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[#1a1a1a] mb-3">
              Certifications &mdash; honest version
            </h2>
            <p>
              Our underlying infrastructure providers (Supabase, Stripe,
              Cloudflare, Railway, Vercel) are SOC 2 Type II and ISO 27001
              certified — that protects the platform layer.
            </p>
            <p className="mt-3">
              <strong>Pebble itself is not yet certified.</strong> We&apos;re
              following the standard SaaS path: implement controls first
              (done — encryption, access logs, per-user isolation, breach
              SOP), engage Vanta or Drata for continuous monitoring (next),
              then schedule the SOC 2 Type II audit (~9 months out). We&apos;ll
              publish the certifications here when they&apos;re real.
            </p>
            <p className="mt-3">
              We&apos;d rather wait and tell you the truth than slap badges
              on the site we haven&apos;t earned.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[#1a1a1a] mb-3">
              Get the signed DPA
            </h2>
            <p>
              Email{" "}
              <a href="mailto:web@getpebble.net?subject=DPA%20Request" className="underline hover:text-[#1a1a1a] transition-colors">
                web@getpebble.net
              </a>{" "}
              with your account email and company name. We&apos;ll send the
              current Pebble DPA, pre-filled with your details, for
              counter-signature inside one business day.
            </p>
            <p className="mt-3 text-sm text-[#1a1a1a]/55">
              For other questions: <Link href="/privacy" className="underline hover:text-[#1a1a1a]">Privacy Policy</Link>{" "}
              · <Link href="/terms" className="underline hover:text-[#1a1a1a]">Terms of Service</Link>
            </p>
          </section>
        </div>
      </MarketingProse>
    </MarketingShell>
  );
}
