"use client";
import { motion } from "framer-motion";
import Image from "next/image";
import Link from "next/link";
import { RefCode } from "@/components/ui/RefCode";
import { ImgRefTag } from "@/components/ui/ImgRefTag";
import { ABOUT_REF_CODE, ABOUT_HEADING, ABOUT_BODY } from "@/content/site";

export function About() {
  return (
    <section id="about" className="relative py-20 sm:py-28 border-t border-white/5">
      <div className="mx-auto grid max-w-6xl gap-12 px-6 lg:grid-cols-2 lg:items-center">
        <motion.div
          initial={{ opacity: 0, x: -32 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        >
          <RefCode accent>{ABOUT_REF_CODE} // ABOUT</RefCode>
          <h2 className="mt-3 stencil text-5xl sm:text-6xl">{ABOUT_HEADING}</h2>
          <div className="mt-6 space-y-4 text-base text-body">
            {ABOUT_BODY.map((para, i) => (
              <p key={i}>{para}</p>
            ))}
          </div>
          <div className="mt-7">
            <Link href="/contact" className="btn-primary">
              TALK TO US
            </Link>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 32 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.8, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          className="relative aspect-[4/5] overflow-hidden border border-white/10"
        >
          <Image
            src="https://images.unsplash.com/photo-1632823469850-2f77dd9c7f93?auto=format&fit=crop&w=1400&q=70"
            alt=""
            fill
            sizes="(min-width: 1024px) 50vw, 100vw"
            className="object-cover"
            style={{ filter: "grayscale(0.5) contrast(1.1)" }}
          />
          <ImgRefTag code="IMG-REF-00001" />
        </motion.div>
      </div>
    </section>
  );
}
