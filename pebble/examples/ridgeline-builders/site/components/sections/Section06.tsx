export default function FooterAnchoredClean() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — name + links */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8 mb-10">

          {/* Business identity */}
          <div className="flex-shrink-0">
            <p className="text-slate-100 text-sm font-semibold tracking-wide" data-pebble-id="pb-b7cd40">
              Ridgeline Builders
            </p>
            <p className="text-slate-500 text-xs mt-1 leading-relaxed max-w-xs" data-pebble-id="pb-13e713">
              Licensed general contractor serving Boise, ID — remodels, additions, and outdoor living.
            </p>
          </div>

          {/* Navigation links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              
              <li data-pebble-id="pb-80364b">
                <a
                  href="#services"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-a4fd7c">
                  Services
                </a>
              </li>
              
              <li data-pebble-id="pb-54e491">
                <a
                  href="#gallery"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-ee8148">
                  Our Work
                </a>
              </li>
              
              <li data-pebble-id="pb-f249f6">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-8a5e57">
                  Get an Estimate
                </a>
              </li>
              
              <li data-pebble-id="pb-a69fcd">
                <a
                  href="tel:+12085550187"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-772ef6">
                  Call Us
                </a>
              </li>
              
            </ul>
          </nav>

        </div>

        {/* Bottom row — divider + copyright */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-slate-600 text-xs" data-pebble-id="pb-ab9c7c">
            &copy; 2025 Ridgeline Builders. All rights reserved.
          </p>
          <p className="text-slate-700 text-xs" data-pebble-id="pb-879fb9">
            Licensed &amp; insured
          </p>
        </div>

      </div>
    </footer>
  );
}
