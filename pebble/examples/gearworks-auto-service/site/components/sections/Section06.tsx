export default function FooterAnchoredClean() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — name + links */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8 mb-10">

          {/* Business identity */}
          <div className="flex-shrink-0">
            <p className="text-slate-100 text-sm font-semibold tracking-wide" data-pebble-id="pb-7e09af">
              Gearworks Auto Service
            </p>
            <p className="text-slate-500 text-xs mt-1 leading-relaxed max-w-xs" data-pebble-id="pb-d7882a">
              ASE-certified auto repair shop serving Columbus, OH.
            </p>
          </div>

          {/* Navigation links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              
              <li data-pebble-id="pb-13384b">
                <a
                  href="#services"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-9e7b74">
                  Services
                </a>
              </li>
              
              <li data-pebble-id="pb-813d7e">
                <a
                  href="#gallery"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-492daf">
                  Our Work
                </a>
              </li>
              
              <li data-pebble-id="pb-491f9a">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-a82510">
                  Book Service
                </a>
              </li>
              
              <li data-pebble-id="pb-759659">
                <a
                  href="tel:6145550192"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-df0983">
                  Call Us
                </a>
              </li>
              
            </ul>
          </nav>

        </div>

        {/* Bottom row — divider + copyright */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-slate-600 text-xs" data-pebble-id="pb-2832c6">
            &copy; 2025 Gearworks Auto Service. All rights reserved.
          </p>
          <p className="text-slate-700 text-xs" data-pebble-id="pb-23b9d7">
            Licensed &amp; insured
          </p>
        </div>

      </div>
    </footer>
  );
}
