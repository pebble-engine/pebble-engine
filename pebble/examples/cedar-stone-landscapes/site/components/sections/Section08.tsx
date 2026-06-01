export default function FooterAnchoredClean() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — name + links */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8 mb-10">

          {/* Business identity */}
          <div className="flex-shrink-0">
            <p className="text-slate-100 text-sm font-semibold tracking-wide" data-pebble-id="pb-43dfb2">
              Cedar & Stone Landscapes
            </p>
            <p className="text-slate-500 text-xs mt-1 leading-relaxed max-w-xs" data-pebble-id="pb-5ba78f">
              Licensed and insured landscape design, lawn care, and hardscape construction in Raleigh, NC.
            </p>
          </div>

          {/* Navigation links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              
              <li data-pebble-id="pb-d3f7cd">
                <a
                  href="#services"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-7edac6">
                  Services
                </a>
              </li>
              
              <li data-pebble-id="pb-032ab3">
                <a
                  href="#gallery"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-0c9d98">
                  Our Work
                </a>
              </li>
              
              <li data-pebble-id="pb-69d28a">
                <a
                  href="#about"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-2c9ac5">
                  About
                </a>
              </li>
              
              <li data-pebble-id="pb-81e849">
                <a
                  href="#coverage"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-f9fd14">
                  Service Area
                </a>
              </li>
              
              <li data-pebble-id="pb-5e7a59">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-6aa416">
                  Contact
                </a>
              </li>
              
            </ul>
          </nav>

        </div>

        {/* Bottom row — divider + copyright */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-slate-600 text-xs" data-pebble-id="pb-1edb0f">
            &copy; 2025 Cedar & Stone Landscapes. All rights reserved.
          </p>
          <p className="text-slate-700 text-xs" data-pebble-id="pb-3bb74c">
            Licensed &amp; insured
          </p>
        </div>

      </div>
    </footer>
  );
}
