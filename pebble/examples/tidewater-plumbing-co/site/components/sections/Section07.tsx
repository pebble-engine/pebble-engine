export default function FooterAnchoredClean() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — name + links */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8 mb-10">

          {/* Business identity */}
          <div className="flex-shrink-0">
            <p className="text-slate-100 text-sm font-semibold tracking-wide" data-pebble-id="pb-d53666">
              Tidewater Plumbing Co.
            </p>
            <p className="text-slate-500 text-xs mt-1 leading-relaxed max-w-xs" data-pebble-id="pb-062a0c">
              Licensed & insured plumbing — SE Portland, serving the metro and inner suburbs.
            </p>
          </div>

          {/* Navigation links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              
              <li data-pebble-id="pb-5667d9">
                <a
                  href="#services"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-4657c7">
                  Services
                </a>
              </li>
              
              <li data-pebble-id="pb-75bb7c">
                <a
                  href="#about"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-0f78d1">
                  About Us
                </a>
              </li>
              
              <li data-pebble-id="pb-c34936">
                <a
                  href="#coverage"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-bf523f">
                  Service Area
                </a>
              </li>
              
              <li data-pebble-id="pb-eed396">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-d24871">
                  Get a Quote
                </a>
              </li>
              
              <li data-pebble-id="pb-2ee8a1">
                <a
                  href="tel:+15035550187"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-d11122">
                  Emergency
                </a>
              </li>
              
            </ul>
          </nav>

        </div>

        {/* Bottom row — divider + copyright */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-slate-600 text-xs" data-pebble-id="pb-06a829">
            &copy; 2025 Tidewater Plumbing Co.. All rights reserved.
          </p>
          <p className="text-slate-700 text-xs" data-pebble-id="pb-5badd5">
            Licensed &amp; insured
          </p>
        </div>

      </div>
    </footer>
  );
}
