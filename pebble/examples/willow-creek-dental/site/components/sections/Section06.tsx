export default function FooterAnchoredClean() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — name + links */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8 mb-10">

          {/* Business identity */}
          <div className="flex-shrink-0">
            <p className="text-slate-100 text-sm font-semibold tracking-wide" data-pebble-id="pb-0cb559">
              Willow Creek Dental
            </p>
            <p className="text-slate-500 text-xs mt-1 leading-relaxed max-w-xs" data-pebble-id="pb-7d78c0">
              Family dental practice in Maplewood, NJ — unhurried care for every age.
            </p>
          </div>

          {/* Navigation links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              
              <li data-pebble-id="pb-1069ce">
                <a
                  href="#services"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-164b90">
                  Services
                </a>
              </li>
              
              <li data-pebble-id="pb-605859">
                <a
                  href="#process"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-346d01">
                  How It Works
                </a>
              </li>
              
              <li data-pebble-id="pb-cbb65e">
                <a
                  href="#about"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-a3fbd7">
                  About Us
                </a>
              </li>
              
              <li data-pebble-id="pb-d41063">
                <a
                  href="#testimonials"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-4e25c4">
                  Patient Reviews
                </a>
              </li>
              
              <li data-pebble-id="pb-fcb4a8">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-4e46a1">
                  Book an Appointment
                </a>
              </li>
              
            </ul>
          </nav>

        </div>

        {/* Bottom row — divider + copyright */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-slate-600 text-xs" data-pebble-id="pb-bdcd23">
            &copy; 2025 Willow Creek Dental. All rights reserved.
          </p>
          <p className="text-slate-700 text-xs" data-pebble-id="pb-1e4aa6">
            Licensed &amp; insured
          </p>
        </div>

      </div>
    </footer>
  );
}
