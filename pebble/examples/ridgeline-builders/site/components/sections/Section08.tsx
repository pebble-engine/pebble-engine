export default function FooterAnchoredClean() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — name + links */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8 mb-10">

          {/* Business identity */}
          <div className="flex-shrink-0">
            <p className="text-slate-100 text-sm font-semibold tracking-wide" data-pebble-id="pb-8efff3">
              Ridgeline Builders
            </p>
            <p className="text-slate-500 text-xs mt-1 leading-relaxed max-w-xs" data-pebble-id="pb-904b7c">
              Licensed general contractor serving Boise, ID and the Treasure Valley.
            </p>
          </div>

          {/* Navigation links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              
              <li data-pebble-id="pb-12c59b">
                <a
                  href="#services"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-c6e2be">
                  Services
                </a>
              </li>
              
              <li data-pebble-id="pb-8305d9">
                <a
                  href="#gallery"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-ac0d2f">
                  Our Work
                </a>
              </li>
              
              <li data-pebble-id="pb-e9dff5">
                <a
                  href="#about"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-d06356">
                  About
                </a>
              </li>
              
              <li data-pebble-id="pb-382626">
                <a
                  href="#coverage"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-739ad1">
                  Service Area
                </a>
              </li>
              
              <li data-pebble-id="pb-ad5bcd">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-7bda6b">
                  Free Estimate
                </a>
              </li>
              
            </ul>
          </nav>

        </div>

        {/* Bottom row — divider + copyright */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-slate-600 text-xs" data-pebble-id="pb-4db74b">
            &copy; 2025 Ridgeline Builders. All rights reserved.
          </p>
          <p className="text-slate-700 text-xs" data-pebble-id="pb-cb741b">
            Licensed &amp; insured
          </p>
        </div>

      </div>
    </footer>
  );
}
