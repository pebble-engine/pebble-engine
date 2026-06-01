export default function FooterAnchoredClean() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — name + links */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8 mb-10">

          {/* Business identity */}
          <div className="flex-shrink-0">
            <p className="text-slate-100 text-sm font-semibold tracking-wide" data-pebble-id="pb-83eccd">
              Gearworks Auto Service
            </p>
            <p className="text-slate-500 text-xs mt-1 leading-relaxed max-w-xs" data-pebble-id="pb-02939d">
              ASE-certified auto repair shop in Columbus, OH — transparent, insured, and customer-first.
            </p>
          </div>

          {/* Navigation links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              
              <li data-pebble-id="pb-0ae79e">
                <a
                  href="#services"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-a58d2b">
                  Services
                </a>
              </li>
              
              <li data-pebble-id="pb-7efc66">
                <a
                  href="#about"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-03fced">
                  About
                </a>
              </li>
              
              <li data-pebble-id="pb-5233b0">
                <a
                  href="#coverage"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-dbfc81">
                  Service Area
                </a>
              </li>
              
              <li data-pebble-id="pb-6b77ad">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-b96e83">
                  Contact
                </a>
              </li>
              
            </ul>
          </nav>

        </div>

        {/* Bottom row — divider + copyright */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-slate-600 text-xs" data-pebble-id="pb-c7cdf8">
            &copy; 2025 Gearworks Auto Service. All rights reserved.
          </p>
          <p className="text-slate-700 text-xs" data-pebble-id="pb-d1f23f">
            Licensed &amp; insured
          </p>
        </div>

      </div>
    </footer>
  );
}
