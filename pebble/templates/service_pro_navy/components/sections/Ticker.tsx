import { TICKER_WORDS } from "@/content/site";

/**
 * Infinite linear marquee. Words are duplicated once so the translateX(-50%)
 * wrap is seamless. CSS animation lives in tailwind.config.ts as `marquee`.
 */
export function Ticker() {
  if (!TICKER_WORDS.length) return null;
  const doubled = [...TICKER_WORDS, ...TICKER_WORDS];

  return (
    <section
      aria-label="Categories"
      className="relative overflow-hidden border-y border-border bg-card/30 py-5"
    >
      <div className="flex w-max animate-marquee gap-10 whitespace-nowrap px-6">
        {doubled.map((word, i) => (
          <span
            key={`${word}-${i}`}
            className="inline-flex items-center gap-3 font-display text-xl font-semibold tracking-tight text-fg/80 sm:text-2xl"
          >
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-primary" />
            {word}
          </span>
        ))}
      </div>
    </section>
  );
}
