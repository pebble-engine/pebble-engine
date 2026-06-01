export default function FooterAnchoredClean() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — name + links */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8 mb-10">

          {/* Business identity */}
          <div className="flex-shrink-0">
            <p className="text-slate-100 text-sm font-semibold tracking-wide" data-pebble-id="pb-9dcc71">
              Northpeak Heating & Air
            </p>
            <p className="text-slate-500 text-xs mt-1 leading-relaxed max-w-xs" data-pebble-id="pb-e40f60">
              Licensed HVAC contractor serving Denver and the Front Range — flat-rate pricing, NATE-certified technicians.
            </p>
          </div>

          {/* Navigation links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              
              <li data-pebble-id="pb-c2a4c6">
                <a
                  href="#services"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-f04363">
                  Services
                </a>
              </li>
              
              <li data-pebble-id="pb-50973e">
                <a
                  href="#about"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-5fdd66">
                  About
                </a>
              </li>
              
              <li data-pebble-id="pb-2d614b">
                <a
                  href="#coverage"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-f1a13e">
                  Service Area
                </a>
              </li>
              
              <li data-pebble-id="pb-157c38">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-8982a6">
                  Emergency Service
                </a>
              </li>
              
              <li data-pebble-id="pb-6aca04">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-a0e29f">
                  Contact
                </a>
              </li>
              
            </ul>
          </nav>

        </div>

        {/* Bottom row — divider + copyright */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-slate-600 text-xs" data-pebble-id="pb-796532">
            &copy; 2025 Northpeak Heating & Air. All rights reserved.
          </p>
          <p className="text-slate-700 text-xs" data-pebble-id="pb-d146df">
            Licensed &amp; insured
          </p>
        </div>

      </div>
    </footer>
  );
}
