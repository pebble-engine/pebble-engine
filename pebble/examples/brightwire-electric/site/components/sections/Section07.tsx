export default function FooterAnchoredClean() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — name + links */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8 mb-10">

          {/* Business identity */}
          <div className="flex-shrink-0">
            <p className="text-slate-100 text-sm font-semibold tracking-wide" data-pebble-id="pb-d23aed">
              Brightwire Electric
            </p>
            <p className="text-slate-500 text-xs mt-1 leading-relaxed max-w-xs" data-pebble-id="pb-22ac62">
              Licensed master electrician serving Austin, TX and Travis County — panels, EV chargers, lighting, generators.
            </p>
          </div>

          {/* Navigation links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              
              <li data-pebble-id="pb-5ee9bf">
                <a
                  href="#services"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-639a9f">
                  Services
                </a>
              </li>
              
              <li data-pebble-id="pb-416635">
                <a
                  href="#about"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-953a8f">
                  About
                </a>
              </li>
              
              <li data-pebble-id="pb-e7f324">
                <a
                  href="#coverage"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-c3eeb2">
                  Service Area
                </a>
              </li>
              
              <li data-pebble-id="pb-87ae4e">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-4bb135">
                  Get a Quote
                </a>
              </li>
              
            </ul>
          </nav>

        </div>

        {/* Bottom row — divider + copyright */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-slate-600 text-xs" data-pebble-id="pb-d8eca9">
            &copy; 2025 Brightwire Electric. All rights reserved.
          </p>
          <p className="text-slate-700 text-xs" data-pebble-id="pb-c9519c">
            Licensed &amp; insured
          </p>
        </div>

      </div>
    </footer>
  );
}
