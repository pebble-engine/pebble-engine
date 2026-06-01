export default function FooterAnchoredClean() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — name + links */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8 mb-10">

          {/* Business identity */}
          <div className="flex-shrink-0">
            <p className="text-slate-100 text-sm font-semibold tracking-wide" data-pebble-id="pb-6d3f8b">
              Ridgeline Builders
            </p>
            <p className="text-slate-500 text-xs mt-1 leading-relaxed max-w-xs" data-pebble-id="pb-c1dc0c">
              Licensed general contractor serving Boise, ID and the Treasure Valley
            </p>
          </div>

          {/* Navigation links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              
              <li data-pebble-id="pb-894575">
                <a
                  href="#services"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-8468ea">
                  Services
                </a>
              </li>
              
              <li data-pebble-id="pb-d9dbbe">
                <a
                  href="#gallery"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-1b7851">
                  Our Work
                </a>
              </li>
              
              <li data-pebble-id="pb-1cf422">
                <a
                  href="#about"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-59918f">
                  About
                </a>
              </li>
              
              <li data-pebble-id="pb-b1e7ed">
                <a
                  href="#coverage"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-827fbd">
                  Service Area
                </a>
              </li>
              
              <li data-pebble-id="pb-1cbebd">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-0b921f">
                  Get an Estimate
                </a>
              </li>
              
            </ul>
          </nav>

        </div>

        {/* Bottom row — divider + copyright */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-slate-600 text-xs" data-pebble-id="pb-0236ce">
            &copy; 2025 Ridgeline Builders. All rights reserved.
          </p>
          <p className="text-slate-700 text-xs" data-pebble-id="pb-27b5b8">
            Licensed &amp; insured
          </p>
        </div>

      </div>
    </footer>
  );
}
