import Link from "next/link";

/**
 * Light-themed navbar — Pebble brand version.
 *
 * Different from the engine's liquid-glass chip (reserved for generated
 * sites). Pebble's own marketing site uses a quiet horizontal navbar
 * with hairline separator below. Per brand book pattern #2.
 */
export function Navbar() {
  return (
    <header className="absolute top-0 inset-x-0 z-50 border-b border-mist bg-sand/80 backdrop-blur-sm">
      <div className="max-w-6xl mx-auto px-6 lg:px-12 py-4 flex items-center justify-between">
        {/* Wordmark — lowercase, Inter Bold, Pebble Stone color */}
        <Link
          href="/"
          className="
            text-xl font-bold tracking-tight text-stone
            rounded-sm
            focus-visible:outline-none focus-visible:ring-2
            focus-visible:ring-river/40 focus-visible:ring-offset-2
            focus-visible:ring-offset-sand
          "
          aria-label="Pebble home"
        >
          pebble
        </Link>

        <nav className="flex items-center gap-6 text-sm">
          <Link
            href="#how-it-works"
            className="
              text-stone/70 hover:text-stone transition-colors
              rounded-sm
              focus-visible:outline-none focus-visible:ring-2
              focus-visible:ring-river/40 focus-visible:ring-offset-2
              focus-visible:ring-offset-sand
            "
          >
            How it works
          </Link>
          <Link
            href="#pricing"
            className="
              hidden sm:inline-block
              text-stone/70 hover:text-stone transition-colors
              rounded-sm
              focus-visible:outline-none focus-visible:ring-2
              focus-visible:ring-river/40 focus-visible:ring-offset-2
              focus-visible:ring-offset-sand
            "
          >
            Pricing
          </Link>
          <Link
            href="#waitlist"
            className="
              bg-river text-sand
              px-4 py-2 rounded-button text-sm font-medium
              hover:bg-stone transition-colors
              focus-visible:outline-none focus-visible:ring-2
              focus-visible:ring-river/40 focus-visible:ring-offset-2
              focus-visible:ring-offset-sand
            "
          >
            Join the waitlist
          </Link>
        </nav>
      </div>
    </header>
  );
}
