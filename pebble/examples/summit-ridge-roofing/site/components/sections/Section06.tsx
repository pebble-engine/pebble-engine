export default function FooterAnchoredClean() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — name + links */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8 mb-10">

          {/* Business identity */}
          <div className="flex-shrink-0">
            <p className="text-slate-100 text-sm font-semibold tracking-wide" data-pebble-id="pb-5dc94e">
              Summit Ridge Roofing
            </p>
            <p className="text-slate-500 text-xs mt-1 leading-relaxed max-w-xs" data-pebble-id="pb-08cc99">
              Licensed roofing contractor serving Kansas City, MO and surrounding communities.
            </p>
          </div>

          {/* Navigation links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              
              <li data-pebble-id="pb-a87811">
                <a
                  href="#services"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-10d0e7">
                  Services
                </a>
              </li>
              
              <li data-pebble-id="pb-faac64">
                <a
                  href="#gallery"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-538b2b">
                  Our Work
                </a>
              </li>
              
              <li data-pebble-id="pb-d596cf">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-06f729">
                  Free Inspection
                </a>
              </li>
              
              <li data-pebble-id="pb-da9dfa">
                <a
                  href="#services"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-4f0ea5">
                  Insurance Help
                </a>
              </li>
              
              <li data-pebble-id="pb-9d7635">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-f117b6">
                  Contact Us
                </a>
              </li>
              
            </ul>
          </nav>

        </div>

        {/* Bottom row — divider + copyright */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-slate-600 text-xs" data-pebble-id="pb-5f1ffb">
            &copy; 2025 Summit Ridge Roofing. All rights reserved.
          </p>
          <p className="text-slate-700 text-xs" data-pebble-id="pb-2aabc6">
            Licensed &amp; insured
          </p>
        </div>

      </div>
    </footer>
  );
}
