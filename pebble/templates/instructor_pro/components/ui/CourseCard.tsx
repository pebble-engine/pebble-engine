import Link from "next/link";
import type { Course } from "@/content/site";
import { cn } from "@/lib/cn";

/**
 * Course card with the signature 4px left accent bar that widens to 5px and
 * changes color on hover (gray -> red, or amber for featured cards) per the
 * training_authority DNA notes.
 */
export function CourseCard({ course, className }: { course: Course; className?: string }) {
  return (
    <Link
      href={`/contact?course=${encodeURIComponent(course.name)}`}
      className={cn(
        "course-card group block rounded-2xl border border-border bg-card pl-7 pr-6 py-6 transition-all duration-200 hover:border-accent/40 hover:-translate-y-1",
        course.featured && "course-card--featured",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-bg",
        className,
      )}
    >
      <span className="course-card__bar" aria-hidden="true" />
      <div className="flex items-center justify-between gap-3 mb-3">
        <span className={cn(
          "inline-flex items-center rounded-full border px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wide-15",
          course.featured
            ? "border-[hsl(var(--accent-warm))]/40 bg-[hsl(var(--accent-warm))]/10 text-[hsl(var(--accent-warm-light))]"
            : "border-accent/40 bg-accent/10 text-accent",
        )}>
          {course.level}
        </span>
        <span className="text-[11px] font-medium uppercase tracking-wide-12 text-subtle">
          {course.duration}
        </span>
      </div>
      <h3 className="font-display text-2xl font-extrabold uppercase tracking-headline text-fg">
        {course.name}
      </h3>
      <p className="mt-2.5 text-sm text-body leading-relaxed">{course.description}</p>
      <span className="mt-4 inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wide-12 text-accent">
        Enroll
        <ArrowIcon className="transition-transform group-hover:translate-x-1" />
      </span>
    </Link>
  );
}

function ArrowIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      width="12"
      height="12"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M5 12h14M13 5l7 7-7 7" />
    </svg>
  );
}
