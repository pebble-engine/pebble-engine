import Link from "next/link";

const EFFECTIVE_DATE = "May 22, 2026";

/**
 * Data Processing Addendum (DPA) stub page.
 *
 * Most early-stage SaaS handles DPAs "on request" rather than shipping a
 * self-serve PDF. That's honest, and it matches Pebble's current process:
 * email Marc, get a signed copy back. This page describes what's in a
 * typical Pebble DPA and how to request one — without inventing a contract
 * we don't have ready to send yet.
 */
export default function DpaPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-3xl px-6 py-16">
        {/* Back link */}
        <div className="mb-10">
          <Link
            href="/landing"
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            ← Back to Pebble
          </Link>
        </div>

        <h1 className="font-display text-4xl font-bold tracking-tight text-foreground mb-2">
          Data Processing Addendum
        </h1>
        <p className="text-sm text-muted-foreground mb-12">Effective {EFFECTIVE_DATE}</p>

        <div className="space-y-10 text-base leading-relaxed text-foreground/80">
          <section>
            <p>
              If your business processes personal data of EU, UK, or California residents
              through Pebble, you may need a signed Data Processing Addendum (&ldquo;DPA&rdquo;)
              from us as your processor. We&apos;re happy to provide one.
            </p>
          </section>

          <section>
            <h2 className="font-display text-xl font-semibold text-foreground mb-3">
              How to request a DPA
            </h2>
            <p className="mb-3">
              Email{" "}
              <a
                href="mailto:web@getpebble.net?subject=DPA%20request"
                className="underline hover:text-foreground transition-colors"
              >
                web@getpebble.net
              </a>{" "}
              with the subject &ldquo;DPA request&rdquo;. Please include:
            </p>
            <ul className="list-disc pl-5 space-y-1">
              <li>The legal name of your business (the controller)</li>
              <li>The country or region your customers are in</li>
              <li>A contact email for the signed copy</li>
            </ul>
            <p className="mt-3">
              We typically turn around a signed DPA within 5 business days. There&apos;s no
              fee — it&apos;s part of being a customer.
            </p>
          </section>

          <section>
            <h2 className="font-display text-xl font-semibold text-foreground mb-3">
              What&apos;s in a typical Pebble DPA
            </h2>
            <p className="mb-3">
              Our standard DPA tracks the structure of the GDPR Article 28 model clauses and
              includes the EU Standard Contractual Clauses (SCCs) where transfers occur. In
              plain language, it covers:
            </p>
            <ul className="list-disc pl-5 space-y-2">
              <li>
                <strong>Roles.</strong> You are the data controller; Pebble is your data
                processor. We process personal data only on your documented instructions.
              </li>
              <li>
                <strong>Purpose and duration.</strong> Processing is limited to operating the
                Pebble service for you, and only for as long as you have an account.
              </li>
              <li>
                <strong>Confidentiality.</strong> Personnel with access to your data are bound
                to confidentiality.
              </li>
              <li>
                <strong>Security measures.</strong> HTTPS in transit, encryption at rest (via
                Supabase), least-privilege access, rate limiting, and incident response
                practices.
              </li>
              <li>
                <strong>Sub-processors.</strong> The current list is below; we&apos;ll give
                advance notice of changes.
              </li>
              <li>
                <strong>Data subject requests.</strong> If your end users exercise GDPR or
                CCPA rights, we&apos;ll assist within reasonable timeframes.
              </li>
              <li>
                <strong>Breach notification.</strong> We notify you without undue delay if we
                become aware of a personal-data breach affecting your data.
              </li>
              <li>
                <strong>Deletion or return.</strong> On termination, we delete or return
                personal data per the deletion process described in our{" "}
                <Link
                  href="/privacy"
                  className="underline hover:text-foreground transition-colors"
                >
                  Privacy Policy
                </Link>
                .
              </li>
              <li>
                <strong>International transfers.</strong> Where transfers leave the EU/EEA or
                UK, the SCCs apply between us and our sub-processors.
              </li>
            </ul>
          </section>

          <section>
            <h2 className="font-display text-xl font-semibold text-foreground mb-3">
              Current sub-processors
            </h2>
            <p className="mb-3">
              Pebble uses the following sub-processors. Each is a major infrastructure
              provider with its own published GDPR posture and (where applicable) SOC 2 or
              ISO 27001 certifications. Pebble inherits those platform-level controls — we do
              not claim them as our own.
            </p>
            <div className="overflow-hidden rounded-xl border border-border">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-muted/40">
                    <th className="py-3 px-4 text-left font-medium text-muted-foreground">
                      Provider
                    </th>
                    <th className="py-3 px-4 text-left font-medium text-muted-foreground">
                      Purpose
                    </th>
                    <th className="py-3 px-4 text-left font-medium text-muted-foreground">
                      Region
                    </th>
                  </tr>
                </thead>
                <tbody className="text-foreground/80">
                  <tr className="border-b border-border">
                    <td className="py-3 px-4 font-medium text-foreground">Supabase</td>
                    <td className="py-3 px-4">
                      Authentication, primary database, file storage
                    </td>
                    <td className="py-3 px-4">United States / EU</td>
                  </tr>
                  <tr className="border-b border-border">
                    <td className="py-3 px-4 font-medium text-foreground">Stripe</td>
                    <td className="py-3 px-4">Payment processing, subscriptions</td>
                    <td className="py-3 px-4">United States</td>
                  </tr>
                  <tr className="border-b border-border">
                    <td className="py-3 px-4 font-medium text-foreground">Resend</td>
                    <td className="py-3 px-4">Transactional email (welcome, reset, replies)</td>
                    <td className="py-3 px-4">United States</td>
                  </tr>
                  <tr className="border-b border-border">
                    <td className="py-3 px-4 font-medium text-foreground">Cloudflare</td>
                    <td className="py-3 px-4">
                      Hosting for published customer sites and edge caching
                    </td>
                    <td className="py-3 px-4">Global edge</td>
                  </tr>
                  <tr className="border-b border-border">
                    <td className="py-3 px-4 font-medium text-foreground">Railway</td>
                    <td className="py-3 px-4">Pebble application hosting</td>
                    <td className="py-3 px-4">United States</td>
                  </tr>
                  <tr>
                    <td className="py-3 px-4 font-medium text-foreground">Vercel</td>
                    <td className="py-3 px-4">Pebble web frontend hosting</td>
                    <td className="py-3 px-4">United States</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p className="mt-3 text-sm text-muted-foreground">
              We&apos;ll keep this list current. If we add or remove a sub-processor, we&apos;ll
              update this page and notify customers under a signed DPA in advance of the
              change taking effect.
            </p>
          </section>

          <section>
            <h2 className="font-display text-xl font-semibold text-foreground mb-3">
              What this page is not
            </h2>
            <p>
              This page is a summary, not the DPA itself. It is not a contract on its own.
              The signed addendum is the binding document; this page exists so you know what
              to expect before requesting one.
            </p>
          </section>

          <section>
            <h2 className="font-display text-xl font-semibold text-foreground mb-3">
              Contact
            </h2>
            <p>
              Pebble Engine &mdash;{" "}
              <a
                href="mailto:web@getpebble.net?subject=DPA%20request"
                className="underline hover:text-foreground transition-colors"
              >
                web@getpebble.net
              </a>
            </p>
          </section>
        </div>

        {/* Footer links */}
        <div className="mt-16 pt-8 border-t border-border flex flex-wrap gap-5 text-sm text-muted-foreground">
          <Link href="/privacy" className="hover:text-foreground transition-colors">
            Privacy Policy
          </Link>
          <Link href="/terms" className="hover:text-foreground transition-colors">
            Terms of Service
          </Link>
          <Link href="/landing" className="hover:text-foreground transition-colors">
            Back to Pebble
          </Link>
          <a
            href="mailto:web@getpebble.net"
            className="hover:text-foreground transition-colors"
          >
            web@getpebble.net
          </a>
        </div>
      </div>
    </div>
  );
}
