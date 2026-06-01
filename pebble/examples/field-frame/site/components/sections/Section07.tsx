export default function FooterMinimalEditorial() {
  return (
    <footer className="bg-neutral-50 border-t border-neutral-900/8 py-12 px-8">
      <div className="container mx-auto max-w-5xl">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-8">

          {/* Left — name + tagline */}
          <div>
            <p className="font-serif text-neutral-900 text-base leading-snug" data-pebble-id="pb-6afbec">
              Field & Frame
            </p>
            <p className="text-neutral-900/35 text-xs font-sans mt-1 leading-relaxed max-w-xs" data-pebble-id="pb-4856f5">
              Residential architecture. Hudson Valley, NY.
            </p>
          </div>

          {/* Center — sparse nav */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              
              <li data-pebble-id="pb-adc5fe">
                <a
                  href="#work"
                  className="text-neutral-900/40 text-xs font-sans tracking-wide hover:text-neutral-900/70 transition-colors" data-pebble-id="pb-d858d4">
                  Work
                </a>
              </li>
              
              <li data-pebble-id="pb-465d67">
                <a
                  href="#studio"
                  className="text-neutral-900/40 text-xs font-sans tracking-wide hover:text-neutral-900/70 transition-colors" data-pebble-id="pb-270841">
                  Studio
                </a>
              </li>
              
              <li data-pebble-id="pb-f20858">
                <a
                  href="#process"
                  className="text-neutral-900/40 text-xs font-sans tracking-wide hover:text-neutral-900/70 transition-colors" data-pebble-id="pb-0b859a">
                  Process
                </a>
              </li>
              
              <li data-pebble-id="pb-d6e001">
                <a
                  href="#contact"
                  className="text-neutral-900/40 text-xs font-sans tracking-wide hover:text-neutral-900/70 transition-colors" data-pebble-id="pb-4db275">
                  Inquiries
                </a>
              </li>
              
            </ul>
          </nav>

          {/* Right — copyright, minimal */}
          <p className="text-neutral-900/25 text-xs font-sans flex-shrink-0" data-pebble-id="pb-bfeb56">
            &copy; 2024
          </p>

        </div>
      </div>
    </footer>
  );
}
