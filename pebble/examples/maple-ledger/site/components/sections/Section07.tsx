export default function FooterAnchoredClean() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — name + links */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8 mb-10">

          {/* Business identity */}
          <div className="flex-shrink-0">
            <p className="text-slate-100 text-sm font-semibold tracking-wide" data-pebble-id="pb-4c27c8">
              Maple & Ledger
            </p>
            <p className="text-slate-500 text-xs mt-1 leading-relaxed max-w-xs" data-pebble-id="pb-b75091">
              CPA and bookkeeping for local small businesses. Millbrook, OH.
            </p>
          </div>

          {/* Navigation links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              
              <li data-pebble-id="pb-00bd6d">
                <a
                  href="#services"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-9eb3c0">
                  Services
                </a>
              </li>
              
              <li data-pebble-id="pb-a50f6a">
                <a
                  href="#process"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-ce88c9">
                  How It Works
                </a>
              </li>
              
              <li data-pebble-id="pb-0e03f8">
                <a
                  href="#about"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-a411f1">
                  About
                </a>
              </li>
              
              <li data-pebble-id="pb-cb1ede">
                <a
                  href="#pricing"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-d6b8d3">
                  Pricing
                </a>
              </li>
              
              <li data-pebble-id="pb-2e752a">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-a5f162">
                  Contact
                </a>
              </li>
              
            </ul>
          </nav>

        </div>

        {/* Bottom row — divider + copyright */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-slate-600 text-xs" data-pebble-id="pb-fea04e">
            &copy; 2025 Maple & Ledger. All rights reserved.
          </p>
          <p className="text-slate-700 text-xs" data-pebble-id="pb-0b50ae">
            Licensed &amp; insured
          </p>
        </div>

      </div>
    </footer>
  );
}
