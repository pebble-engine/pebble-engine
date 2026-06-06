export default function FooterAnchoredClean() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — name + links */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8 mb-10">

          {/* Business identity */}
          <div className="flex-shrink-0">
            <p className="text-slate-100 text-sm font-semibold tracking-wide" data-pebble-id="pb-0cc629">
              Gearworks Auto Service
            </p>
            <p className="text-slate-500 text-xs mt-1 leading-relaxed max-w-xs" data-pebble-id="pb-3c0332">
              ASE-certified auto repair in Columbus, OH — transparent inspections, honest pricing.
            </p>
          </div>

          {/* Navigation links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              
              <li data-pebble-id="pb-cf16a3">
                <a
                  href="#services"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-1c067d">
                  Services
                </a>
              </li>
              
              <li data-pebble-id="pb-e35ecd">
                <a
                  href="#about"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-19ed60">
                  About
                </a>
              </li>
              
              <li data-pebble-id="pb-04233b">
                <a
                  href="#coverage"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-ca7ea9">
                  Service Area
                </a>
              </li>
              
              <li data-pebble-id="pb-18b8d1">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-fdd073">
                  Contact
                </a>
              </li>
              
            </ul>
          </nav>

        </div>

        {/* Bottom row — divider + copyright */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-slate-600 text-xs" data-pebble-id="pb-027f2d">
            &copy; 2025 Gearworks Auto Service. All rights reserved.
          </p>
          <p className="text-slate-700 text-xs" data-pebble-id="pb-567b16">
            Licensed &amp; insured
          </p>
        </div>

      </div>
    </footer>
  );
}
