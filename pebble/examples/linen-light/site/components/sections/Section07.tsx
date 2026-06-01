export default function FooterMinimalEditorial() {
  return (
    <footer className="bg-neutral-50 border-t border-neutral-900/8 py-12 px-8">
      <div className="container mx-auto max-w-5xl">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-8">

          {/* Left — name + tagline */}
          <div>
            <p className="font-serif text-neutral-900 text-base leading-snug" data-pebble-id="pb-8e633c">
              Linen & Light
            </p>
            <p className="text-neutral-900/35 text-xs font-sans mt-1 leading-relaxed max-w-xs" data-pebble-id="pb-f98daa">
              Film wedding photography. Oregon & Northern California.
            </p>
          </div>

          {/* Center — sparse nav */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              
              <li data-pebble-id="pb-cf1cae">
                <a
                  href="#work"
                  className="text-neutral-900/40 text-xs font-sans tracking-wide hover:text-neutral-900/70 transition-colors" data-pebble-id="pb-db8104">
                  Work
                </a>
              </li>
              
              <li data-pebble-id="pb-6a6c6d">
                <a
                  href="#about"
                  className="text-neutral-900/40 text-xs font-sans tracking-wide hover:text-neutral-900/70 transition-colors" data-pebble-id="pb-f44e20">
                  About
                </a>
              </li>
              
              <li data-pebble-id="pb-524110">
                <a
                  href="#rates"
                  className="text-neutral-900/40 text-xs font-sans tracking-wide hover:text-neutral-900/70 transition-colors" data-pebble-id="pb-c7a01f">
                  Rates
                </a>
              </li>
              
              <li data-pebble-id="pb-7e2c39">
                <a
                  href="#contact"
                  className="text-neutral-900/40 text-xs font-sans tracking-wide hover:text-neutral-900/70 transition-colors" data-pebble-id="pb-a0ba0f">
                  Inquire
                </a>
              </li>
              
            </ul>
          </nav>

          {/* Right — copyright, minimal */}
          <p className="text-neutral-900/25 text-xs font-sans flex-shrink-0" data-pebble-id="pb-714332">
            &copy; 2025
          </p>

        </div>
      </div>
    </footer>
  );
}
