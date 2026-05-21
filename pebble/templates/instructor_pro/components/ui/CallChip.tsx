import { cn } from "@/lib/cn";
import { PHONE, PHONE_DISPLAY } from "@/content/site";

/**
 * Shimmer-band "CALL NOW" pill above a tap-to-call phone number. The top
 * label is the marketing chip; the bottom row is the actual `tel:` link.
 */
export function CallChip({ className }: { className?: string }) {
  return (
    <div className={cn("flex flex-col items-center gap-1.5", className)}>
      <span className="shimmer-band inline-flex items-center gap-1.5 rounded-full border border-accent/40 bg-accent/15 px-3 py-1 text-[11px] font-bold uppercase tracking-wide-12 text-accent">
        <PhoneIcon />
        Call Now
      </span>
      <a
        href={`tel:${PHONE.replace(/[^+\d]/g, "")}`}
        className="font-display text-lg font-bold tracking-tight text-fg hover:text-accent transition-colors"
      >
        {PHONE_DISPLAY}
      </a>
    </div>
  );
}

function PhoneIcon() {
  return (
    <svg
      width="11"
      height="11"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
    </svg>
  );
}
