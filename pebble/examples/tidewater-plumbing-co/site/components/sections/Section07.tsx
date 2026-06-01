export default function FooterAnchoredClean() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — name + links */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8 mb-10">

          {/* Business identity */}
          <div className="flex-shrink-0">
            <p className="text-slate-100 text-sm font-semibold tracking-wide" data-pebble-id="pb-bf1623">
              Tidewater Plumbing Co.
            </p>
            <p className="text-slate-500 text-xs mt-1 leading-relaxed max-w-xs" data-pebble-id="pb-715b4a">
              Licensed & insured plumber serving Portland, OR and the inner metro.
            </p>
          </div>

          {/* Navigation links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              
              <li data-pebble-id="pb-ab415e">
                <a
                  href="#services"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-bb7008">
                  Services
                </a>
              </li>
              
              <li data-pebble-id="pb-cfb5b5">
                <a
                  href="#about"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-e9f7c7">
                  About
                </a>
              </li>
              
              <li data-pebble-id="pb-24e235">
                <a
                  href="#coverage"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-e3ae65">
                  Service Area
                </a>
              </li>
              
              <li data-pebble-id="pb-d9e813">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-6de583">
                  Get a Quote
                </a>
              </li>
              
              <li data-pebble-id="pb-418ddf">
                <a
                  href="tel:+15035550198"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-94a371">
                  Emergency Line
                </a>
              </li>
              
            </ul>
          </nav>

        </div>

        {/* Bottom row — divider + copyright */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-slate-600 text-xs" data-pebble-id="pb-2229d3">
            &copy; 2025 Tidewater Plumbing Co.. All rights reserved.
          </p>
          <p className="text-slate-700 text-xs" data-pebble-id="pb-eb3fdb">
            Licensed &amp; insured
          </p>
        </div>

      </div>
    </footer>
  );
}
