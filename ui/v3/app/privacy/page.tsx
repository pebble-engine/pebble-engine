import Link from "next/link";
import { MarketingShell, MarketingProse } from "@/components/marketing-shell";

const EFFECTIVE_DATE = "May 18, 2026";

export default function PrivacyPage() {
  return (
    <MarketingShell>
      <MarketingProse>
        <h1 className="text-4xl font-semibold tracking-tight text-[#1a1a1a] mb-2">
          Privacy Policy
        </h1>
        <p className="text-sm text-[#1a1a1a]/55 mb-12">Effective {EFFECTIVE_DATE}</p>

        <div className="space-y-10 text-base leading-relaxed text-[#1a1a1a]/75">
          <section>
            <h2 className="text-xl font-semibold text-[#1a1a1a] mb-3">
              1. Who we are
            </h2>
            <p>
              Pebble Engine (&ldquo;Pebble&rdquo;, &ldquo;we&rdquo;, &ldquo;our&rdquo;) operates
              the website-building platform at{" "}
              <a href="https://pebbleapp.ai" className="underline hover:text-[#1a1a1a] transition-colors">
                pebbleapp.ai
              </a>{" "}
              and its associated services. Questions:{" "}
              <a href="mailto:web@getpebble.net" className="underline hover:text-[#1a1a1a] transition-colors">
                web@getpebble.net
              </a>
              .
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[#1a1a1a] mb-3">
              2. What we collect and why
            </h2>
            <div className="space-y-4">
              <div>
                <p className="font-medium text-[#1a1a1a]">Account information</p>
                <p>
                  When you sign up, we collect your email address and, optionally, your first name
                  and display name. Your password is hashed by Supabase — we never see it in
                  plaintext.
                </p>
              </div>
              <div>
                <p className="font-medium text-[#1a1a1a]">Questionnaire answers</p>
                <p>
                  To build your site, we collect the information you enter into the Pebble
                  questionnaire (business name, industry, services, tone preferences, etc.). This
                  content is used solely to generate your site and is stored in your project files.
                </p>
              </div>
              <div>
                <p className="font-medium text-[#1a1a1a]">Billing information</p>
                <p>
                  If you subscribe to a paid plan, your payment is
                  processed by Stripe. We never see or store your full card number. We do store your
                  Stripe customer ID and subscription status to manage your account.
                </p>
              </div>
              <div>
                <p className="font-medium text-[#1a1a1a]">Usage events</p>
                <p>
                  We record product-level events (e.g., &ldquo;site built&rdquo;,
                  &ldquo;site published&rdquo;) to understand how the product is used. These events
                  record <em>what</em> happened and <em>when</em> — never the content of your site
                  or questionnaire answers.
                </p>
              </div>
              <div>
                <p className="font-medium text-[#1a1a1a]">Email communications</p>
                <p>
                  After your first successful build, we send a short welcome sequence (day 1, 3,
                  and 7) with tips and encouragement. You can reply to any email to unsubscribe from
                  future messages.
                </p>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[#1a1a1a] mb-3">
              3. Third-party services
            </h2>
            <p className="mb-3">
              Pebble uses the following services, each with its own privacy policy:
            </p>
            <ul className="list-disc pl-5 space-y-2">
              <li>
                <strong>Supabase</strong> — authentication, database, and file storage.
              </li>
              <li>
                <strong>Stripe</strong> — payment processing and subscription management.
              </li>
              <li>
                <strong>Resend</strong> — transactional email delivery (welcome, password reset,
                build tips).
              </li>
              <li>
                <strong>Cloudflare</strong> — hosting for your published sites and our own
                infrastructure.
              </li>
              <li>
                <strong>Google / GitHub</strong> — optional OAuth sign-in. We receive only your
                email address and public profile name.
              </li>
              <li>
                <strong>Plausible Analytics</strong> — privacy-friendly traffic analytics on
                pebbleapp.ai. No cookies, no cross-site tracking, no personal data collected.
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[#1a1a1a] mb-3">
              4. Your generated sites
            </h2>
            <p>
              The websites Pebble generates are yours. We store the generated files on our servers
              to power the preview and editor. When you publish a site, Pebble deploys those files
              to Cloudflare Pages on your behalf. We do not sell, share, or use your site content
              for training AI models.
            </p>
            <p className="mt-3">
              <strong>Privacy on generated sites:</strong> By default, Pebble-built sites include
              no third-party tracking scripts. Your visitors are not tracked unless you add your own
              analytics code.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[#1a1a1a] mb-3">
              5. Cookies and local storage
            </h2>
            <p>
              Pebble uses a session cookie to keep you signed in. We do not use advertising cookies
              or third-party tracking pixels on the platform itself.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[#1a1a1a] mb-3">
              6. Data retention and deletion
            </h2>
            <p>
              We keep your data for as long as your account is active. You can delete your account
              at any time from{" "}
              <Link href="/settings" className="underline hover:text-[#1a1a1a] transition-colors">
                Settings → Account
              </Link>
              . Deletion requests enter a 14-day cooling-off period, after which your account, site
              files, and associated data are permanently removed. You can cancel a pending deletion
              during that window.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[#1a1a1a] mb-3">
              7. Your rights (GDPR / CCPA)
            </h2>
            <p className="mb-3">
              Depending on where you live, you may have rights to:
            </p>
            <ul className="list-disc pl-5 space-y-1">
              <li>Access the personal data we hold about you</li>
              <li>Correct inaccurate data</li>
              <li>Request deletion of your data</li>
              <li>Object to or restrict certain processing</li>
              <li>Data portability (a copy of your data in a common format)</li>
            </ul>
            <p className="mt-3">
              Email{" "}
              <a href="mailto:web@getpebble.net" className="underline hover:text-[#1a1a1a] transition-colors">
                web@getpebble.net
              </a>{" "}
              to exercise any of these rights. Account deletion is self-serve via Settings.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[#1a1a1a] mb-3">
              8. Security
            </h2>
            <p>
              We use HTTPS everywhere, store passwords only as Supabase-managed hashes, and apply
              rate limiting to sensitive endpoints. No system is 100% secure; we will notify you
              promptly if we become aware of a breach affecting your data.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[#1a1a1a] mb-3">
              9. Children
            </h2>
            <p>
              Pebble is not directed at children under 13. We do not knowingly collect personal
              data from children.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[#1a1a1a] mb-3">
              10. Changes to this policy
            </h2>
            <p>
              We may update this policy as the product evolves. We will notify you by email before
              material changes take effect. Continued use after the effective date constitutes
              acceptance.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[#1a1a1a] mb-3">
              11. Contact
            </h2>
            <p>
              Pebble Engine &mdash;{" "}
              <a href="mailto:web@getpebble.net" className="underline hover:text-[#1a1a1a] transition-colors">
                web@getpebble.net
              </a>
            </p>
          </section>
        </div>

        {/* Footer links */}
        <div className="mt-16 pt-8 border-t border-stone-200 flex flex-wrap gap-5 text-sm text-[#1a1a1a]/55">
          <Link href="/terms" className="hover:text-[#1a1a1a] transition-colors">
            Terms of Service
          </Link>
          <Link href="/" className="hover:text-[#1a1a1a] transition-colors">
            Back to Pebble
          </Link>
          <a href="mailto:web@getpebble.net" className="hover:text-[#1a1a1a] transition-colors">
            web@getpebble.net
          </a>
        </div>
      </MarketingProse>
    </MarketingShell>
  );
}
