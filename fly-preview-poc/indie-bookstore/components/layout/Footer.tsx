import Link from "next/link";

export function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer className="border-t border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-text-secondary)]">
      <div className="max-w-7xl mx-auto px-6 md:px-12 lg:px-16 py-16 grid gap-12 md:grid-cols-3">
        <div>
          <h3 className="text-lg font-medium text-[var(--color-text-primary)] mb-2" data-pebble-id="pb-7fe13e">Indie Bookstore</h3>
          <p className="text-sm mb-4" data-pebble-id="pb-aa065b">Curated collections, community events, and a cozy reading space in the heart of Portland.</p>
          <a href="tel:[BUSINESS PHONE]" className="text-[var(--color-accent)] hover:opacity-80 transition-opacity block mb-2" style={{ fontSize: "16px" }} data-pebble-id="pb-945118">[BUSINESS PHONE]</a>
          <a href="mailto:[EMAIL]" className="text-[var(--color-accent)] hover:opacity-80 transition-opacity block mb-4" style={{ fontSize: "16px" }} data-pebble-id="pb-94496d">[EMAIL]</a>
          <p className="text-sm" data-pebble-id="pb-12998c">[ADDRESS]</p>
        </div>

        <div>
          <h3 className="text-lg font-medium text-[var(--color-text-primary)] mb-4" data-pebble-id="pb-324b2c">Explore</h3>
          <ul className="space-y-2 text-sm">
            <li data-pebble-id="pb-658957"><Link href="/" className="hover:text-[var(--color-text-primary)] transition-colors font-medium">Home</Link></li>
            <li data-pebble-id="pb-a1c497"><Link href="/services" className="hover:text-[var(--color-text-primary)] transition-colors font-medium">Services</Link></li>
            <li data-pebble-id="pb-af850c"><Link href="/about" className="hover:text-[var(--color-text-primary)] transition-colors font-medium">About</Link></li>
            <li data-pebble-id="pb-1c295d"><Link href="/contact" className="hover:text-[var(--color-text-primary)] transition-colors font-medium">Contact</Link></li>
            <li data-pebble-id="pb-f4ec36"><Link href="/faq" className="hover:text-[var(--color-text-primary)] transition-colors font-medium">FAQ</Link></li>
            <li data-pebble-id="pb-1672c3"><Link href="/privacy" className="hover:text-[var(--color-text-primary)] transition-colors font-medium">Privacy Policy</Link></li>
            <li data-pebble-id="pb-c3c25f"><Link href="/terms" className="hover:text-[var(--color-text-primary)] transition-colors font-medium">Terms of Service</Link></li>
          </ul>
        </div>

        <div>
          <h3 className="text-lg font-medium text-[var(--color-text-primary)] mb-4" data-pebble-id="pb-6d1993">Hours & Social</h3>
          <p className="text-sm mb-4" data-pebble-id="pb-4796f6">Mon–Fri 9–8 · Sat 10–6 · Sun 11–5</p>
          <p className="text-xs mt-8" data-pebble-id="pb-f34bfa">© {year} Indie Bookstore. All rights reserved.</p>
          <p className="text-xs text-[var(--color-text-muted)] mt-4" data-pebble-id="pb-e7e932">iii</p>
        </div>
      </div>
      <div className="border-t border-[var(--color-border)] mt-12 pt-6 text-xs text-[var(--color-text-muted)] px-6 md:px-12 lg:px-16 flex flex-col md:flex-row justify-between items-center gap-2">
        <span data-pebble-id="pb-23b69e">Built with <a href="https://pebbleapp.ai" className="text-[var(--color-accent)] hover:opacity-80" target="_blank" rel="noopener noreferrer" data-pebble-id="pb-200a7e">Pebble</a></span>
        <div className="flex gap-4">
          <Link href="/privacy" className="hover:text-[var(--color-text-secondary)] transition-colors">Privacy</Link>
          <Link href="/terms" className="hover:text-[var(--color-text-secondary)] transition-colors">Terms</Link>
        </div>
      </div>
    </footer>
  );
}