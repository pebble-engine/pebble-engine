import Link from "next/link";
import { MarketingShell, MarketingProse } from "@/components/marketing-shell";

/**
 * /trust — Phase 52 (2026-05-22).
 *
 * The full Pebble Trust Charter. Backs every claim on the landing
 * trust seal with the specific control + the file where it lives.
 *
 * Posture: self-attested, third-party-audit roadmap stated honestly.
 * This is the same template Linear, Cal.com, Resend, Plausible used
 * before their SOC 2 audits landed — works because every claim is
 * grounded in code or policy the reader can verify.
 *
 * Effective date and reference ID match the seal component.
 */

const EFFECTIVE_DATE = "May 22, 2026";
const CHARTER_REF = "PEB-TC-2026-05-22";

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
      "Encryption in transit (TLS 1.2+) on every endpoint. Encryption at rest for all account " +
      "data, sentinels, and form submissions via Supabase + Cloudflare R2 / Railway storage. " +
      "Passwords hashed by Supabase Auth with Argon2. Per-user filesystem isolation in the " +
      "engine's output directory.",
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
      "Breach-notification SOP is maintained internally; the notification commitment is part of the DPA.",
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
    evidence: (
      <>
        Implementation: <code className="font-mono text-xs bg-muted px-1 rounded">pebble/server/account.py</code>{" "}
        (<code className="font-mono text-xs bg-muted px-1 rounded">run_delete_account</code>,{" "}
        <code className="font-mono text-xs bg-muted px-1 rounded">run_cancel_deletion</code>).{" "}
        Cooling-off window configurable per <code className="font-mono text-xs bg-muted px-1 rounded">PEBBLE_DELETION_COOLING_DAYS</code>.
      </>
    ),
  },
  {
    id:    "rights-access",
    area:  "Data Rights",
    title: "Access, rectification, portability — handled within timelines",
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
        with your account email. We log every request and the response.
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
        . Generated sites can opt into the same setup; see the analytics integration.
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
    title: "Per-user filesystem + database isolation",
    promise:
      "Each customer's projects live in a per-user directory the engine validates on every " +
      "request. Database row-level security via Supabase RLS prevents cross-tenant reads even " +
      "if an authorization check is missed at the API layer.",
    evidence: (
      <>
        Slug validation in <code className="font-mono text-xs bg-muted px-1 rounded">pebble/security.py</code>{" "}
        (<code className="font-mono text-xs bg-muted px-1 rounded">validate_slug</code>,{" "}
        <code className="font-mono text-xs bg-muted px-1 rounded">require_project_owner</code>).{" "}
        Schema-level RLS policies live in <code className="font-mono text-xs bg-muted px-1 rounded">schema/</code>.
      </>
    ),
  },
  {
    id:    "sec-secrets",
    area:  "Security",
    title: "Secrets never leave the secret channel",
    promise:
      "API keys, OAuth tokens, and webhook secrets are stored only in environment variables — " +
      "never in source, never in the database, never in user-facing UI. Database row encryption " +
      "for any field that holds a third-party credential.",
    evidence:
      "Engine secrets live in .env files (gitignored). Per-project integration credentials, " +
      "when added, will use Supabase Vault for envelope encryption.",
  },
  {
    id:    "sec-audit-roadmap",
    area:  "Security",
    title: "External audit roadmap — honest version",
    promise:
      "Pebble itself is not yet SOC 2 Type II or ISO 27001 certified. We're following the " +
      "standard SaaS path: implement the controls first (done), engage Vanta or Drata for " +
      "continuous monitoring (next milestone), then run a 6-12 month observation period and " +
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
        {/* Document header — matches the seal's effective date + ref ID */}
        <div className="mb-12">
          <p className="text-xs font-bold uppercase tracking-[0.3em] text-[#1a1a1a]/55 mb-3">
            Pebble Trust Charter
          </p>
          <h1 className="text-4xl font-semibold tracking-tight text-[#1a1a1a] mb-2">
            What we commit to, and the proof behind it.
          </h1>
          <p className="text-sm text-[#1a1a1a]/55">
            Effective {EFFECTIVE_DATE} · Reference {CHARTER_REF}
          </p>
        </div>

        {/* Honest framing — no "WE'RE CERTIFIED!!" theatre */}
        <div className="mb-12 p-6 bg-[#1a1a1a]/5 border border-[#1a1a1a]/10 rounded-2xl text-base leading-relaxed text-[#1a1a1a]/80">
          <p className="mb-3">
            <strong className="text-[#1a1a1a]">This charter is self-attested.</strong>{" "}
            Pebble Engine is not yet SOC 2 or ISO 27001 certified — those are real audits we&apos;ll
            pursue once we&apos;ve cleared the revenue + headcount thresholds to fund them well.
            We&apos;ll publish the report and the badge here when they&apos;re real.
          </p>
          <p>
            Until then, this page is the receipts: every claim below points to the specific
            code, policy, or sub-processor that backs it. You don&apos;t need to take our word
            for anything — you can verify each commitment yourself.
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

        {/* Closing block — how to verify + report issues */}
        <section className="mt-16 pt-10 border-t border-[#1a1a1a]/15 space-y-4">
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
          <h2 className="text-xl font-semibold text-[#1a1a1a] pt-4">Changes to this charter</h2>
          <p className="text-base text-[#1a1a1a]/75 leading-relaxed">
            Material changes (new commitment removed or weakened, new sub-processor added) are
            announced to your account email 30 days in advance. Editorial changes (clarifications,
            typo fixes, evidence-link updates) are committed silently — full revision history
            lives in the project&apos;s public Git log.
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
