import { ContactForm } from "@/components/forms/ContactForm";
import { CallChip } from "@/components/ui/CallChip";
import { EMAIL, ADDRESS, HOURS, SERVICE_AREAS } from "@/content/site";

/**
 * Two-column contact: enrollment form on the right, contact details +
 * call chip on the left.
 */
export function Contact() {
  return (
    <section id="contact" className="relative py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-6">
        <div className="grid gap-12 lg:grid-cols-5">
          <div className="lg:col-span-2 space-y-7">
            <div>
              <p className="text-xs font-bold uppercase tracking-wide-15 text-accent">
                Enroll Now
              </p>
              <h2 className="mt-3 font-display text-4xl font-black uppercase tracking-headline text-fg sm:text-5xl">
                Get <span className="text-gold-gradient">Started</span>
              </h2>
              <p className="mt-3 text-base text-muted">
                Send us a message. We'll respond within one business day with the next available class
                and answer any questions about prerequisites.
              </p>
            </div>

            <div className="glass-light rounded-2xl p-6">
              <CallChip className="items-start" />
            </div>

            <ul className="space-y-4 text-sm">
              <ContactRow label="Email">
                <a href={`mailto:${EMAIL}`} className="text-fg/90 hover:text-accent break-all">
                  {EMAIL}
                </a>
              </ContactRow>
              <ContactRow label="Address">
                <span className="text-fg/90">{ADDRESS}</span>
              </ContactRow>
              <ContactRow label="Hours">
                <span className="text-fg/90">{HOURS}</span>
              </ContactRow>
              <ContactRow label="Service Areas">
                <span className="text-fg/90">{SERVICE_AREAS.join(" · ")}</span>
              </ContactRow>
            </ul>
          </div>

          <div className="lg:col-span-3">
            <div className="glass rounded-3xl p-6 sm:p-8">
              <ContactForm />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function ContactRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <li className="grid grid-cols-[7rem_1fr] items-start gap-3">
      <span className="text-[10px] font-bold uppercase tracking-wide-15 text-subtle">
        {label}
      </span>
      <div>{children}</div>
    </li>
  );
}
