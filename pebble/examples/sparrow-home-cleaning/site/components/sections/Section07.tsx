export default function FooterAnchoredClean() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — name + links */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8 mb-10">

          {/* Business identity */}
          <div className="flex-shrink-0">
            <p className="text-slate-100 text-sm font-semibold tracking-wide" data-pebble-id="pb-5f5ecc">
              Sparrow Home Cleaning
            </p>
            <p className="text-slate-500 text-xs mt-1 leading-relaxed max-w-xs" data-pebble-id="pb-97434a">
              Professional home and office cleaning in Minneapolis, MN — insured, bonded, and satisfaction guaranteed.
            </p>
          </div>

          {/* Navigation links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              
              <li data-pebble-id="pb-37de48">
                <a
                  href="#services"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-df0733">
                  Services
                </a>
              </li>
              
              <li data-pebble-id="pb-62f833">
                <a
                  href="#about"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-277ddb">
                  About Us
                </a>
              </li>
              
              <li data-pebble-id="pb-f70ad5">
                <a
                  href="#coverage"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-efa922">
                  Service Areas
                </a>
              </li>
              
              <li data-pebble-id="pb-d9af4b">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-6de682">
                  Book Online
                </a>
              </li>
              
              <li data-pebble-id="pb-d2b1e8">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-13e88b">
                  Contact
                </a>
              </li>
              
            </ul>
          </nav>

        </div>

        {/* Bottom row — divider + copyright */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-slate-600 text-xs" data-pebble-id="pb-e68b7f">
            &copy; 2025 Sparrow Home Cleaning. All rights reserved.
          </p>
          <p className="text-slate-700 text-xs" data-pebble-id="pb-e2fff2">
            Licensed &amp; insured
          </p>
        </div>

      </div>
    </footer>
  );
}
