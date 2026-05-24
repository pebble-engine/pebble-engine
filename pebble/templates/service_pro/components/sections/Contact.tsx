import { ContactForm } from "@/components/forms/ContactForm";
import { CallChip } from "@/components/ui/CallChip";
import { Reveal } from "@/components/ui/Reveal";
import {
  EMAIL,
  ADDRESS,
  HOURS,
  SERVICE_AREAS,
} from "@/content/site";

export function Contact() {
  return (
    <section id="contact" className="relative py-20 sm:py-28">
      <Reveal>
      <div className="mx-auto max-w-6xl px-6">
        <div className="grid gap-12 lg:grid-cols-5">
          <div className="lg:col-span-2 space-y-7">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
                Get in touch
              </p>
              <h2 className="mt-3 font-display text-4xl font-bold tracking-tight text-fg sm:text-5xl">
                Free <span className="gradient-text">inspection</span>.
              </h2>
              <p className="mt-3 text-base text-muted">
                Tell us what's bugging you. We'll respond within one business day.
              </p>
            </div>

            <div className="glass-card rounded-2xl p-6">
              <CallChip className="items-start" />
            </div>

            <ul className="space-y-4 text-sm">
              <ContactRow label="Email">
                <a href={`mailto:${EMAIL}`} className="text-fg/90 hover:text-primary break-all">
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
            <div className="glass-card rounded-3xl p-6 sm:p-8">
              <ContactForm />
            </div>
          </div>
        </div>
      </div>
      </Reveal>
    </section>
  );
}

function ContactRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <li className="grid grid-cols-[6rem_1fr] items-start gap-3">
      <span className="text-[10px] font-semibold uppercase tracking-[0.18em] text-subtle">
        {label}
      </span>
      <div>{children}</div>
    </li>
  );
}
