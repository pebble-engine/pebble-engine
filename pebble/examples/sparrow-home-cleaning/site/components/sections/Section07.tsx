export default function FooterAnchoredClean() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — name + links */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8 mb-10">

          {/* Business identity */}
          <div className="flex-shrink-0">
            <p className="text-slate-100 text-sm font-semibold tracking-wide" data-pebble-id="pb-6b48bb">
              Sparrow Home Cleaning
            </p>
            <p className="text-slate-500 text-xs mt-1 leading-relaxed max-w-xs" data-pebble-id="pb-853562">
              Residential and small office cleaning service in Minneapolis, MN
            </p>
          </div>

          {/* Navigation links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              
              <li data-pebble-id="pb-ac21ee">
                <a
                  href="#services"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-36e5f1">
                  Services
                </a>
              </li>
              
              <li data-pebble-id="pb-db7a56">
                <a
                  href="#about"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-91d9a7">
                  About
                </a>
              </li>
              
              <li data-pebble-id="pb-70481c">
                <a
                  href="#coverage"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-5dbd47">
                  Service Area
                </a>
              </li>
              
              <li data-pebble-id="pb-9e4b7e">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-ef352d">
                  Book Online
                </a>
              </li>
              
              <li data-pebble-id="pb-f9f877">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-9944a7">
                  Contact
                </a>
              </li>
              
            </ul>
          </nav>

        </div>

        {/* Bottom row — divider + copyright */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-slate-600 text-xs" data-pebble-id="pb-09ecbb">
            &copy; 2025 Sparrow Home Cleaning. All rights reserved.
          </p>
          <p className="text-slate-700 text-xs" data-pebble-id="pb-f74820">
            Licensed &amp; insured
          </p>
        </div>

      </div>
    </footer>
  );
}
