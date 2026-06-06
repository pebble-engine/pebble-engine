export default function FooterAnchoredClean() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — name + links */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8 mb-10">

          {/* Business identity */}
          <div className="flex-shrink-0">
            <p className="text-slate-100 text-sm font-semibold tracking-wide" data-pebble-id="pb-2c6a44">
              Cedar & Stone Landscapes
            </p>
            <p className="text-slate-500 text-xs mt-1 leading-relaxed max-w-xs" data-pebble-id="pb-e04005">
              Licensed landscaping and hardscape contractor serving the Raleigh–Durham Triangle, NC.
            </p>
          </div>

          {/* Navigation links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              
              <li data-pebble-id="pb-33f53b">
                <a
                  href="#services"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-4074dc">
                  Services
                </a>
              </li>
              
              <li data-pebble-id="pb-48e30a">
                <a
                  href="#gallery"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-2f5e3e">
                  Our Work
                </a>
              </li>
              
              <li data-pebble-id="pb-c7601d">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-55e2da">
                  Free Consultation
                </a>
              </li>
              
              <li data-pebble-id="pb-460197">
                <a
                  href="tel:+19195550182"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-3a1363">
                  Call Us
                </a>
              </li>
              
            </ul>
          </nav>

        </div>

        {/* Bottom row — divider + copyright */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-slate-600 text-xs" data-pebble-id="pb-6f26f5">
            &copy; 2025 Cedar & Stone Landscapes. All rights reserved.
          </p>
          <p className="text-slate-700 text-xs" data-pebble-id="pb-36e94e">
            Licensed &amp; insured
          </p>
        </div>

      </div>
    </footer>
  );
}
