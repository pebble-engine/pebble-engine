import Link from "next/link";
import { MarketingShell, MarketingProse } from "@/components/marketing-shell";

/**
 * /trust — Phase 52 (2026-05-22), revised 52b (NLM critique applied).
 *
 * v1 of this page named specific Python file paths as evidence (e.g.
 * pebble/server/account.py). NLM critique: that's a security smell —
 * a buyer can't verify the code anyway, but an attacker gets a treasure
 * map of which modules to probe.
 *
 * v2 swaps file paths for plain-language control descriptions. Every
 * claim still has evidence; the evidence is now "what we do," not "where
 * to look in our source." Same level of honesty, less attack-surface
 * disclosure.
 *
 * Other v2 changes:
 *   - "Charter" → "Commitment" everywhere (less authoritative-sounding)
 *   - Added "Security questionnaire (CAIQ)" section — standard SaaS
 *     pre-SOC 2 artifact for B2B procurement
 *   - Added EU Representative contact for GDPR Article 27 compliance
 *   - Removed cert-style reference ID (was "PEB-TC-2026-05-22" — too
 *     mimicry-ish; effective date alone is the version stamp)
 */

const EFFECTIVE_DATE = "May 22, 2026";

type Commitment = {
  id:        string;
  area:      "GDPR" | "Data Rights" | "Security";
  title:     string;
  promise:   string;
  evidence:  React.ReactNode;
};

const COMMITMENTS: Commitment[] = [
  // ── GDPR ──────────────────────────────────────────────────────────────
  {
    id:    "gdpr-roles",
    area:  "GDPR",
    title: "Processor / Controller roles documented (Article 28)",
    promise:
      "You are the data controller for the personal data Pebble handles on your behalf. " +
      "Pebble is the data processor. Our DPA spells out the roles and obligations both ways.",
    evidence: (
      <>
        See the <Link href="/dpa" className="underline hover:no-underline">Data Processing Addendum</Link>.
        Signed copy available on request from{" "}
        <a href="mailto:web@getpebble.net?subject=DPA%20Request" className="underline hover:no-underline">
          web@getpebble.net
        </a>
        .
      </>
    ),
  },
  {
    id:    "gdpr-security",
    area:  "GDPR",
    title: "Appropriate technical and organisational measures (Article 32)",
    promise:
      "TLS 1.2+ in transit on every endpoint. Encryption at rest for account data, sentinels, " +
      "and form submissions. Passwords hashed via Supabase Auth (Argon2). Per-tenant filesystem " +
      "isolation in the engine. Database row-level security via Supabase RLS prevents cross-" +
      "tenant reads even if an authorisation check is missed at the API layer.",
    evidence: (
      <>
        Sub-processor list in <Link href="/dpa" className="underline hover:no-underline">/dpa</Link>;{" "}
        each provider is independently SOC 2 Type II certified.
      </>
    ),
  },
  {
    id:    "gdpr-breach",
    area:  "GDPR",
    title: "Personal data breach notification (Articles 33 & 34)",
    promise:
      "On confirmation of a personal data breach affecting your data, we notify you without " +
      "undue delay — target 48 hours, well inside the regulatory 72-hour window. Notification " +
      "includes scope, affected data categories, mitigations, and remediation timeline.",
    evidence:
      "Internal breach-notification SOP. The notification commitment is part of the DPA we sign with you.",
  },
  {
    id:    "gdpr-transfers",
    area:  "GDPR",
    title: "International transfers via Standard Contractual Clauses",
    promise:
      "EEA → US data transfers happen through our sub-processors (Supabase, Stripe, Resend, " +
      "Cloudflare, Railway, Vercel, Anthropic, Google, OpenRouter), all of which operate under " +
      "the EU SCCs.",
    evidence: (
      <>
        Sub-processor regions + privacy-policy links in{" "}
        <Link href="/dpa" className="underline hover:no-underline">/dpa</Link>.
      </>
    ),
  },
  {
    id:    "gdpr-eu-rep",
    area:  "GDPR",
    title: "EU Representative (Article 27)",
    promise:
      "Pebble Engine processes personal data of EEA / UK residents and is therefore subject to " +
      "the appointment of an EU Representative under GDPR Article 27 and a UK Representative " +
      "under the UK GDPR. Both appointments are in process; until they're finalised, EU and UK " +
      "data subjects can address rights requests to the contact below and we will route them " +
      "appropriately under reasonable timelines.",
    evidence: (
      <>
        Interim contact:{" "}
        <a href="mailto:web@getpebble.net?subject=EU%20Rep%20Inquiry" className="underline hover:no-underline">
          web@getpebble.net
        </a>
        . Formal Representative appointment listed here once executed.
      </>
    ),
  },

  // ── Data Rights ───────────────────────────────────────────────────────
  {
    id:    "rights-delete",
    area:  "Data Rights",
    title: "Account deletion with a real cooling-off window",
    promise:
      "Request deletion from your account settings. The request enters a 14-day cooling-off " +
      "window so you can cancel by mistake without losing your work. After the window, all " +
      "associated personal data is purged from our systems and sub-processor cleanups run that " +
      "same week.",
    evidence:
      "Implemented end-to-end with audit logging. Cooling-off length configurable via deployment env (default 14 days).",
  },
  {
    id:    "rights-access",
    area:  "Data Rights",
    title: "Access, rectification, portability — within GDPR timelines",
    promise:
      "Requests for access (what data we hold), rectification (fix incorrect data), or " +
      "portability (export your projects in machine-readable form) are honoured within " +
      "the GDPR-mandated 30-day window. Most requests are fulfilled within 5 business days.",
    evidence: (
      <>
        Email{" "}
        <a href="mailto:web@getpebble.net?subject=Data%20Subject%20Request" className="underline hover:no-underline">
          web@getpebble.net
        </a>{" "}
        with your account email. We log every request and the response for our own audit trail.
      </>
    ),
  },
  {
    id:    "rights-no-tracking",
    area:  "Data Rights",
    title: "Cookieless analytics — no consent banner needed",
    promise:
      "Pebble's own product analytics (visit counts, page views) run on Plausible, which is " +
      "fully cookieless and aggregated. We don't fingerprint browsers, don't store IPs, and " +
      "don't sell anonymised behaviour data to anyone.",
    evidence: (
      <>
        Plausible is GDPR / PECR / CCPA compliant by design — see{" "}
        <a href="https://plausible.io/data-policy" target="_blank" rel="noopener noreferrer" className="underline hover:no-underline">
          plausible.io/data-policy
        </a>
        . Generated sites can opt into the same setup via the analytics integration.
      </>
    ),
  },

  // ── Security ──────────────────────────────────────────────────────────
  {
    id:    "sec-platform",
    area:  "Security",
    title: "Built on SOC 2 / ISO 27001 infrastructure",
    promise:
      "Every layer Pebble depends on — auth, database, payments, email, CDN, hosting, AI — is " +
      "operated by a SOC 2 Type II and / or ISO 27001 certified provider. That doesn't make " +
      "Pebble itself certified, but it means the platform under the application is auditable.",
    evidence:
      "Supabase (SOC 2 Type II + ISO 27001 + HIPAA), Stripe (SOC 2 Type II + ISO 27001 + PCI DSS), " +
      "Cloudflare (SOC 2 Type II + ISO 27001), Railway (SOC 2 Type II), Vercel (SOC 2 Type II), " +
      "Anthropic (SOC 2 Type II), Resend (SOC 2 Type II).",
  },
  {
    id:    "sec-access",
    area:  "Security",
    title: "Tenant isolation by default",
    promise:
      "Each customer's projects live in a per-tenant directory the engine validates on every " +
      "request via a centralised slug guard. Database row-level security (Supabase RLS) prevents " +
      "cross-tenant reads even if an authorisation check is missed at the API layer — defence " +
      "in depth.",
    evidence:
      "Slug guard + ownership-check helpers are the entry point for every project mutation. " +
      "Schema-level RLS policies are version-controlled with the rest of our infrastructure code.",
  },
  {
    id:    "sec-secrets",
    area:  "Security",
    title: "Secrets stay in the secret channel",
    promise:
      "API keys, OAuth tokens, and webhook secrets are stored only in environment variables — " +
      "never in source, never in the database, never in user-facing UI. Per-project integration " +
      "credentials, when added, use envelope encryption.",
    evidence:
      "Engine secrets live in .env files outside the repository. Vault-style encryption is in " +
      "place for any third-party credentials we store on a customer's behalf.",
  },
  {
    id:    "sec-audit-roadmap",
    area:  "Security",
    title: "External audit roadmap — honest version",
    promise:
      "Pebble itself is not yet SOC 2 Type II or ISO 27001 certified. We're following the " +
      "standard SaaS path: implement the controls first (done), engage Vanta or Drata for " +
      "continuous monitoring (next milestone), then run the 6-12 month observation period and " +
      "external audit. Targeting our first SOC 2 Type II report at ~$500K ARR.",
    evidence:
      "We'll publish the audit report and badge here when it's real. Until then this section " +
      "stays honest about what's certified (infrastructure) and what's not (Pebble itself).",
  },
];

const AREA_ORDER: Commitment["area"][] = ["GDPR", "Data Rights", "Security"];

export default function TrustPage() {
  const byArea = Object.fromEntries(
    AREA_ORDER.map((area) => [area, COMMITMENTS.filter((c) => c.area === area)]),
  ) as Record<Commitment["area"], Commitment[]>;

  return (
    <MarketingShell>
      <MarketingProse>
        {/* Document header */}
        <div className="mb-12">
          <p className="text-xs font-bold uppercase tracking-[0.3em] text-[#1a1a1a]/55 mb-3">
            Pebble Trust Commitment
          </p>
          <h1 className="text-4xl font-semibold tracking-tight text-[#1a1a1a] mb-2">
            What we commit to, and the proof behind it.
          </h1>
          <p className="text-sm text-[#1a1a1a]/55">
            Effective {EFFECTIVE_DATE} · Self-attested by Pebble Engine
          </p>
        </div>

        {/* Honest framing — no audit theatre */}
        <div className="mb-12 p-6 bg-[#1a1a1a]/5 border border-[#1a1a1a]/10 rounded-2xl text-base leading-relaxed text-[#1a1a1a]/80">
          <p className="mb-3">
            <strong className="text-[#1a1a1a]">This is a self-attested commitment.</strong>{" "}
            Pebble Engine is not yet SOC 2 or ISO 27001 certified — those are real audits we&apos;ll
            pursue once we&apos;ve cleared the revenue + headcount thresholds to fund them well.
            We&apos;ll publish the report and the badge here when they&apos;re real.
          </p>
          <p>
            Until then, this page is the receipts: every claim below is described in plain
            language so you can verify, ask follow-ups, and request artefacts (DPA, security
            questionnaire) for your own procurement process. We&apos;d rather be honest about
            where we are than mock up a certification we haven&apos;t earned.
          </p>
        </div>

        {/* Commitments grouped by area */}
        <div className="space-y-12">
          {AREA_ORDER.map((area) => (
            <section key={area}>
              <div className="flex items-center gap-3 mb-6">
                <h2 className="text-2xl font-semibold text-[#1a1a1a]">{area}</h2>
                <span className="text-xs font-bold uppercase tracking-widest text-[#1a1a1a]/40">
                  {byArea[area].length} commitments
                </span>
              </div>
              <ol className="space-y-6">
                {byArea[area].map((c) => (
                  <li key={c.id} className="border-l-2 border-[#1a1a1a]/15 pl-5 sm:pl-6">
                    <h3 className="text-lg font-semibold text-[#1a1a1a] mb-2">{c.title}</h3>
                    <p className="text-base text-[#1a1a1a]/75 leading-relaxed mb-2">{c.promise}</p>
                    <p className="text-sm text-[#1a1a1a]/55 leading-relaxed">
                      <span className="font-bold uppercase tracking-widest text-[10px] mr-2 text-[#1a1a1a]/40">
                        Evidence
                      </span>
                      {c.evidence}
                    </p>
                  </li>
                ))}
              </ol>
            </section>
          ))}
        </div>

        {/* Security questionnaire (CAIQ) — pre-SOC2 standard artefact */}
        <section className="mt-16 pt-10 border-t border-[#1a1a1a]/15 space-y-4">
          <h2 className="text-xl font-semibold text-[#1a1a1a]">Security questionnaire (CAIQ)</h2>
          <p className="text-base text-[#1a1a1a]/75 leading-relaxed">
            For B2B procurement teams: we maintain a completed CSA CAIQ
            (Cloud Security Alliance Consensus Assessments Initiative Questionnaire) —
            the standard self-attested security questionnaire that&apos;s the practical
            substitute for SOC 2 at our stage. Available on request from{" "}
            <a href="mailto:web@getpebble.net?subject=CAIQ%20Request" className="underline hover:no-underline">
              web@getpebble.net
            </a>
            . We&apos;ll send the current version (PDF or Excel) inside one business day,
            no NDA required for the questionnaire itself.
          </p>
        </section>

        {/* Working toward — honest near-term security roadmap. These are
            real, free, third-party-listed credentials that Pebble can
            pursue NOW without paying for an audit. Listed publicly so
            anyone evaluating Pebble can hold us to the timeline. */}
        <section className="mt-12 pt-10 border-t border-[#1a1a1a]/15 space-y-4">
          <h2 className="text-xl font-semibold text-[#1a1a1a]">Working toward — next 30 days</h2>
          <p className="text-base text-[#1a1a1a]/75 leading-relaxed">
            We don&apos;t want to talk about security without taking concrete
            steps. Below are the public, third-party-listed credentials
            we&apos;re actively pursuing right now. Each one is free and
            verifiable.
          </p>
          <ul className="space-y-4 text-base text-[#1a1a1a]/75 leading-relaxed">
            <li>
              <strong className="text-[#1a1a1a]">CSA STAR Level 1</strong>
              {" "}— Cloud Security Alliance&apos;s public security registry. We&apos;ll
              submit our CAIQ to CSA and be listed on{" "}
              <a href="https://cloudsecurityalliance.org/star/registry/" target="_blank" rel="noopener noreferrer" className="underline hover:no-underline">
                their registry
              </a>
              . Public, verifiable, no theatre.
            </li>
            <li>
              <strong className="text-[#1a1a1a]">OpenSSF Best Practices Badge</strong>
              {" "}— Open Source Security Foundation badge for projects that
              meet a documented set of secure-development practices. We&apos;ll
              be listed on{" "}
              <a href="https://www.bestpractices.dev/" target="_blank" rel="noopener noreferrer" className="underline hover:no-underline">
                bestpractices.dev
              </a>{" "}
              with the answers we submitted visible to anyone.
            </li>
            <li>
              <strong className="text-[#1a1a1a]">Mozilla Observatory + SSL Labs A+ grades</strong>
              {" "}— third-party scans of our HTTP security headers, TLS
              configuration, and content security policy. Re-scanned on
              every deploy; we&apos;ll display the live grade once it&apos;s
              A+ across both.
            </li>
            <li>
              <strong className="text-[#1a1a1a]">SOC 2 Type II</strong>
              {" "}— the real audit. Vanta or Drata for continuous monitoring
              at ~$200K ARR, full Type II audit at ~$500K ARR. We&apos;ll
              publish the report and the badge here when it&apos;s real.
            </li>
          </ul>
          <p className="text-sm text-[#1a1a1a]/55 leading-relaxed pt-2">
            We&apos;re shipping these because we&apos;d rather earn a real
            credential than slap a mocked-up one on the site. If you&apos;re
            evaluating Pebble and want a status update on any of the above,
            email{" "}
            <a href="mailto:web@getpebble.net?subject=Security%20Roadmap" className="underline hover:no-underline">
              web@getpebble.net
            </a>
            .
          </p>
        </section>

        {/* Reporting a security issue */}
        <section className="mt-12 pt-10 border-t border-[#1a1a1a]/15 space-y-4">
          <h2 className="text-xl font-semibold text-[#1a1a1a]">Reporting a security issue</h2>
          <p className="text-base text-[#1a1a1a]/75 leading-relaxed">
            Found something concerning? Email{" "}
            <a href="mailto:web@getpebble.net?subject=Security%20Issue" className="underline hover:no-underline">
              web@getpebble.net
            </a>
            {" "}with details. We acknowledge security reports within 24 hours and will keep you
            updated through remediation. We don&apos;t currently run a paid bug-bounty program;
            we DO send genuine thanks and a Pebble t-shirt for any report that materially
            improves our security posture.
          </p>
          <h2 className="text-xl font-semibold text-[#1a1a1a] pt-4">Changes to this commitment</h2>
          <p className="text-base text-[#1a1a1a]/75 leading-relaxed">
            Material changes (a commitment removed or weakened, a new sub-processor added) are
            announced to your account email 30 days in advance. Editorial changes (clarifications,
            typo fixes, evidence-link updates) are committed silently — full revision history
            lives in the project&apos;s Git log.
          </p>
          <h2 className="text-xl font-semibold text-[#1a1a1a] pt-4">Related documents</h2>
          <ul className="space-y-2 text-base text-[#1a1a1a]/75">
            <li>
              <Link href="/privacy" className="underline hover:no-underline">
                Privacy Policy
              </Link>
              {" "}— what we collect, how we use it, your rights
            </li>
            <li>
              <Link href="/dpa" className="underline hover:no-underline">
                Data Processing Addendum
              </Link>
              {" "}— sub-processor table + signed-copy request
            </li>
            <li>
              <Link href="/terms" className="underline hover:no-underline">
                Terms of Service
              </Link>
              {" "}— account ownership, generated-content rights, liability
            </li>
          </ul>
        </section>
      </MarketingProse>
    </MarketingShell>
  );
}
