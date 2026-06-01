export default function FooterAnchoredClean() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — name + links */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8 mb-10">

          {/* Business identity */}
          <div className="flex-shrink-0">
            <p className="text-slate-100 text-sm font-semibold tracking-wide" data-pebble-id="pb-4973b8">
              Summit Ridge Roofing
            </p>
            <p className="text-slate-500 text-xs mt-1 leading-relaxed max-w-xs" data-pebble-id="pb-877dc5">
              Licensed roofing contractor serving Kansas City, MO — replacements, storm repair, and insurance claims.
            </p>
          </div>

          {/* Navigation links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              
              <li data-pebble-id="pb-b0b724">
                <a
                  href="#services"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-587474">
                  Services
                </a>
              </li>
              
              <li data-pebble-id="pb-abc8bb">
                <a
                  href="#about"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-e60eaa">
                  About
                </a>
              </li>
              
              <li data-pebble-id="pb-ce57c0">
                <a
                  href="#coverage"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-8b6e09">
                  Service Area
                </a>
              </li>
              
              <li data-pebble-id="pb-20dc1b">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-349137">
                  Free Estimate
                </a>
              </li>
              
              <li data-pebble-id="pb-5f72cd">
                <a
                  href="tel:+18165550180"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-97fa6c">
                  Call Us
                </a>
              </li>
              
            </ul>
          </nav>

        </div>

        {/* Bottom row — divider + copyright */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-slate-600 text-xs" data-pebble-id="pb-6032f6">
            &copy; 2025 Summit Ridge Roofing. All rights reserved.
          </p>
          <p className="text-slate-700 text-xs" data-pebble-id="pb-2f0163">
            Licensed &amp; insured
          </p>
        </div>

      </div>
    </footer>
  );
}
