"use client";
import { motion } from "framer-motion";
import { CourseCard } from "@/components/ui/CourseCard";
import { COURSES } from "@/content/site";

/**
 * Course/class catalog — the conversion section. Three-column grid of
 * cards with the signature widening left bar (gray default, amber for
 * featured) per the training_authority DNA.
 */
export function Courses() {
  if (!COURSES.length) return null;

  return (
    <section id="courses" className="relative py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-xs font-bold uppercase tracking-wide-15 text-accent">
            Curriculum
          </p>
          <h2 className="mt-3 font-display text-4xl font-black uppercase tracking-headline text-fg sm:text-5xl">
            Pick Your <span className="text-gold-gradient">Path</span>
          </h2>
          <p className="mt-4 text-base text-muted">
            Every course is built on the same foundation, then layered for the level you're at.
            Tap any class to enroll or ask questions.
          </p>
        </div>

        <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {COURSES.map((course, i) => (
            <motion.div
              key={course.id}
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.5, delay: i * 0.06, ease: "easeOut" }}
            >
              <CourseCard course={course} />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
