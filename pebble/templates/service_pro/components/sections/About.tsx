"use client";
import { motion } from "framer-motion";
import Image from "next/image";
import { Reveal } from "@/components/ui/Reveal";
import { Button } from "@/components/ui/Button";
import { ABOUT_HEADING, ABOUT_BODY, RATING_VALUE, RATING_COUNT } from "@/content/site";

export function About() {
  return (
    <section id="about" className="relative py-20 sm:py-28">
      <Reveal>
      <div className="mx-auto grid max-w-6xl gap-12 px-6 lg:grid-cols-2 lg:items-center">
        <motion.div
          initial={{ opacity: 0, x: -16 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        >
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
            About us
          </p>
          <h2 className="mt-3 font-display text-4xl font-bold tracking-tight text-fg sm:text-5xl">
            {ABOUT_HEADING}
          </h2>
          <div className="mt-5 space-y-4 text-base text-body">
            {ABOUT_BODY.map((para, i) => (
              <p key={i}>{para}</p>
            ))}
          </div>
          <div className="mt-7 flex flex-wrap items-center gap-4">
            <Button href="/about" variant="primary" size="md">
              Our story
            </Button>
            <div className="inline-flex items-center gap-2 text-sm text-muted">
              <span className="font-semibold text-fg">{RATING_VALUE}</span> from{" "}
              <span className="text-fg">{RATING_COUNT}</span> reviews
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 16 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
          className="relative aspect-[4/5] overflow-hidden rounded-3xl border border-border"
        >
          <Image
            src="https://images.unsplash.com/photo-1581094271901-8022df4466f9?auto=format&fit=crop&w=1200&q=70"
            alt=""
            fill
            sizes="(min-width: 1024px) 50vw, 100vw"
            className="object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-bg/60 via-transparent to-transparent" />
        </motion.div>
      </div>
      </Reveal>
    </section>
  );
}
