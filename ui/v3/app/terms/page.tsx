import Link from "next/link";

const EFFECTIVE_DATE = "May 18, 2026";

export default function TermsPage() {
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
          Terms of Service
        </h1>
        <p className="text-sm text-muted-foreground mb-12">Effective {EFFECTIVE_DATE}</p>

        <div className="space-y-10 text-base leading-relaxed text-foreground/80">
          <section>
            <h2 className="font-display text-xl font-semibold text-foreground mb-3">
              1. About Pebble
            </h2>
            <p>
              Pebble Engine (&ldquo;Pebble&rdquo;, &ldquo;we&rdquo;, &ldquo;us&rdquo;) provides
              an AI-powered website builder at{" "}
              <a href="https://pebbleapp.ai" className="underline hover:text-foreground transition-colors">
                pebbleapp.ai
              </a>
              . By creating an account or using our services, you agree to these Terms.
            </p>
          </section>

          <section>
            <h2 className="font-display text-xl font-semibold text-foreground mb-3">
              2. Your account
            </h2>
            <p>
              You must provide a valid email address and keep your account credentials secure. You
              are responsible for all activity that occurs under your account. Notify us immediately
              at{" "}
              <a href="mailto:web@getpebble.net" className="underline hover:text-foreground transition-colors">
                web@getpebble.net
              </a>{" "}
              if you suspect unauthorised access.
            </p>
          </section>

          <section>
            <h2 className="font-display text-xl font-semibold text-foreground mb-3">
              3. Plans, billing, and trial
            </h2>
            <div className="space-y-4">
              <div>
                <p className="font-medium text-foreground">Free tier</p>
                <p>
                  Free accounts may publish up to 2 sites. The builder and all editing tools are
                  fully available. No payment is required to start.
                </p>
              </div>
              <div>
                <p className="font-medium text-foreground">Paid plans</p>
                <p>
                  Starter ($29/month) and Pro ($59/month) subscriptions unlock unlimited published
                  sites and additional features. Prices are in USD and charged monthly.
                </p>
              </div>
              <div>
                <p className="font-medium text-foreground">Free trial</p>
                <p>
                  When offered, a free trial period lets you use a paid plan before your card is
                  charged. You can cancel during the trial with no charge.
                </p>
              </div>
              <div>
                <p className="font-medium text-foreground">Setup call</p>
                <p>
                  The $99 one-time setup call is a non-refundable purchase of a one-hour live
                  session with the Pebble team. A calendar booking link is sent to your email after
                  payment.
                </p>
              </div>
              <div>
                <p className="font-medium text-foreground">Cancellation</p>
                <p>
                  Cancel your subscription at any time via{" "}
                  <Link href="/settings" className="underline hover:text-foreground transition-colors">
                    Settings → Billing
                  </Link>
                  . Your plan remains active until the end of the current billing period.
                </p>
              </div>
              <div>
                <p className="font-medium text-foreground">Refunds</p>
                <p>
                  We offer a no-questions-asked refund within 7 days of your first charge on a new
                  subscription. Email{" "}
                  <a href="mailto:web@getpebble.net" className="underline hover:text-foreground transition-colors">
                    web@getpebble.net
                  </a>{" "}
                  with your account email to request one.
                </p>
              </div>
            </div>
          </section>

          <section>
            <h2 className="font-display text-xl font-semibold text-foreground mb-3">
              4. What you can build
            </h2>
            <p className="mb-3">
              You may use Pebble to build websites for lawful purposes. You agree not to use Pebble
              to create content that:
            </p>
            <ul className="list-disc pl-5 space-y-1">
              <li>Violates any applicable law or regulation</li>
              <li>Infringes intellectual property rights of any third party</li>
              <li>Contains malware, phishing pages, or fraudulent content</li>
              <li>Harasses, threatens, or deceives others</li>
              <li>Promotes illegal products or services</li>
            </ul>
            <p className="mt-3">
              We reserve the right to suspend accounts or take down content that violates these
              terms.
            </p>
          </section>

          <section>
            <h2 className="font-display text-xl font-semibold text-foreground mb-3">
              5. Your content and intellectual property
            </h2>
            <p>
              You retain ownership of all content you provide (business information, copy, images)
              and the websites Pebble generates for you. By using Pebble you grant us a limited
              licence to store, process, and deploy your content as needed to operate the service.
            </p>
            <p className="mt-3">
              We do not use your site content or questionnaire answers to train AI models.
            </p>
            <p className="mt-3">
              Pebble, its platform code, the Pebble name and branding, and any original content we
              create are our intellectual property. Nothing in these Terms transfers that ownership
              to you.
            </p>
          </section>

          <section>
            <h2 className="font-display text-xl font-semibold text-foreground mb-3">
              6. Service availability
            </h2>
            <p>
              We aim for high availability but do not guarantee uninterrupted service. Scheduled
              maintenance and unexpected outages may occur. We are not liable for losses arising
              from downtime.
            </p>
            <p className="mt-3">
              If your subscription lapses, your published sites will display a reactivation notice
              rather than your normal content until the subscription is renewed.
            </p>
          </section>

          <section>
            <h2 className="font-display text-xl font-semibold text-foreground mb-3">
              7. Limitation of liability
            </h2>
            <p>
              To the maximum extent permitted by law, Pebble is not liable for any indirect,
              incidental, special, or consequential damages arising from your use of (or inability
              to use) the service, including lost profits, lost data, or business interruption —
              even if we have been advised of the possibility of such damages.
            </p>
            <p className="mt-3">
              Our total aggregate liability for any claim related to these Terms or the service
              shall not exceed the amount you paid us in the twelve months preceding the claim.
            </p>
          </section>

          <section>
            <h2 className="font-display text-xl font-semibold text-foreground mb-3">
              8. Disclaimer of warranties
            </h2>
            <p>
              The service is provided &ldquo;as is&rdquo; and &ldquo;as available&rdquo; without
              warranties of any kind, express or implied, including merchantability, fitness for a
              particular purpose, and non-infringement.
            </p>
          </section>

          <section>
            <h2 className="font-display text-xl font-semibold text-foreground mb-3">
              9. Account deletion
            </h2>
            <p>
              You can delete your account at any time from Settings. Deletion requests enter a
              14-day cooling-off period, after which your account and all associated data are
              permanently removed. See our{" "}
              <Link href="/privacy" className="underline hover:text-foreground transition-colors">
                Privacy Policy
              </Link>{" "}
              for details.
            </p>
          </section>

          <section>
            <h2 className="font-display text-xl font-semibold text-foreground mb-3">
              10. Changes to these Terms
            </h2>
            <p>
              We may update these Terms as the product evolves. We will notify you by email before
              material changes take effect. Continued use after the effective date constitutes
              acceptance of the updated Terms.
            </p>
          </section>

          <section>
            <h2 className="font-display text-xl font-semibold text-foreground mb-3">
              11. Governing law
            </h2>
            <p>
              These Terms are governed by the laws of the United States. Any disputes shall be
              resolved through good-faith negotiation; if that fails, through binding arbitration.
            </p>
          </section>

          <section>
            <h2 className="font-display text-xl font-semibold text-foreground mb-3">
              12. Contact
            </h2>
            <p>
              Pebble Engine &mdash;{" "}
              <a href="mailto:web@getpebble.net" className="underline hover:text-foreground transition-colors">
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
          <Link href="/landing" className="hover:text-foreground transition-colors">
            Back to Pebble
          </Link>
          <a href="mailto:web@getpebble.net" className="hover:text-foreground transition-colors">
            web@getpebble.net
          </a>
        </div>
      </div>
    </div>
  );
}
