export function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer className="px-6 lg:px-12 py-12 bg-sand border-t border-mist">
      <div className="max-w-5xl mx-auto flex flex-col md:flex-row gap-6 items-start md:items-center justify-between">
        <div>
          <p className="text-stone font-bold text-lg tracking-tight">pebble</p>
          <p className="brand-mono mt-2 text-stone/40">© {year} Pebble</p>
        </div>
        <nav className="flex gap-6 text-sm text-stone/60">
          <a
            href="#how-it-works"
            className="hover:text-stone transition-colors rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-river/40 focus-visible:ring-offset-2 focus-visible:ring-offset-sand"
          >
            How it works
          </a>
          <a
            href="#pricing"
            className="hover:text-stone transition-colors rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-river/40 focus-visible:ring-offset-2 focus-visible:ring-offset-sand"
          >
            Pricing
          </a>
          <a
            href="#waitlist"
            className="hover:text-stone transition-colors rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-river/40 focus-visible:ring-offset-2 focus-visible:ring-offset-sand"
          >
            Join waitlist
          </a>
        </nav>
      </div>
    </footer>
  );
}
