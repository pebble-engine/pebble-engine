"use client";
import { motion } from "framer-motion";
import Image from "next/image";
import { PulseDot } from "@/components/ui/PulseDot";
import {
  INSTRUCTOR_NAME,
  INSTRUCTOR_TITLE,
  INSTRUCTOR_IMAGE_URL,
  INSTRUCTOR_BIO,
  INSTRUCTOR_CREDENTIALS,
} from "@/content/site";

/**
 * Instructor bio section — major DNA element. Two-column layout:
 *  - Left: 4:5 portrait with gradient bottom mask
 *  - Right: floating glass credentials card that overlaps the portrait
 *           with a red-pulse status dot + bulleted list (gold-glow box-shadow)
 */
export function Instructor() {
  return (
    <section id="instructor" className="relative py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mx-auto max-w-2xl text-center mb-14">
          <p className="text-xs font-bold uppercase tracking-wide-15 text-accent">
            The Instructor
          </p>
          <h2 className="mt-3 font-display text-4xl font-black uppercase tracking-headline text-fg sm:text-5xl">
            Meet Your <span className="text-gold-gradient">Coach</span>
          </h2>
        </div>

        <div className="grid gap-12 lg:grid-cols-12 lg:items-center">
          {/* Portrait — left */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.7, ease: "easeOut" }}
            className="relative lg:col-span-7"
          >
            <div className="relative aspect-[4/5] overflow-hidden rounded-3xl border border-border">
              <Image
                src={INSTRUCTOR_IMAGE_URL}
                alt={INSTRUCTOR_NAME}
                fill
                sizes="(min-width: 1024px) 60vw, 100vw"
                className="object-cover"
                priority={false}
              />
              {/* Gradient bottom mask per DNA */}
              <div className="absolute inset-0 bg-gradient-to-t from-bg/85 via-bg/15 to-transparent" />
            </div>
          </motion.div>

          {/* Credentials card — right, floating glass with red-pulse dot */}
          <motion.aside
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.7, ease: "easeOut", delay: 0.15 }}
            className="lg:col-span-5 lg:-ml-16 lg:mt-12"
          >
            <div className="glass glow-credentials rounded-2xl p-7 sm:p-8">
              <div className="flex items-center gap-2 mb-5">
                <PulseDot />
                <span className="text-[11px] font-bold uppercase tracking-wide-15 text-accent">
                  Currently Teaching
                </span>
              </div>
              <h3 className="font-display text-3xl font-black uppercase tracking-headline text-fg">
                {INSTRUCTOR_NAME}
              </h3>
              <p className="mt-1 text-xs font-bold uppercase tracking-wide-12 text-subtle">
                {INSTRUCTOR_TITLE}
              </p>

              <div className="mt-5 space-y-3.5">
                {INSTRUCTOR_BIO.map((para, i) => (
                  <p key={i} className="text-sm text-body leading-relaxed">
                    {para}
                  </p>
                ))}
              </div>

              <ul className="mt-6 space-y-2.5 border-t border-border pt-5">
                {INSTRUCTOR_CREDENTIALS.map((cred) => (
                  <li key={cred} className="flex items-start gap-2.5 text-sm text-fg/85">
                    <CheckIcon />
                    <span>{cred}</span>
                  </li>
                ))}
              </ul>
            </div>
          </motion.aside>
        </div>
      </div>
    </section>
  );
}

function CheckIcon() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="3"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="mt-0.5 text-[hsl(var(--accent-warm-light))] flex-shrink-0"
      aria-hidden="true"
    >
      <path d="M20 6 9 17l-5-5" />
    </svg>
  );
}
