export default function FooterAnchoredClean() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — name + links */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8 mb-10">

          {/* Business identity */}
          <div className="flex-shrink-0">
            <p className="text-slate-100 text-sm font-semibold tracking-wide" data-pebble-id="pb-0752ad">
              Maple & Hart Law
            </p>
            <p className="text-slate-500 text-xs mt-1 leading-relaxed max-w-xs" data-pebble-id="pb-8b400e">
              Family law practice in Burlington, VT — plain English, no pressure.
            </p>
          </div>

          {/* Navigation links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              
              <li data-pebble-id="pb-b7d8b0">
                <a
                  href="#services"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-1b70a6">
                  Services
                </a>
              </li>
              
              <li data-pebble-id="pb-a9eab7">
                <a
                  href="#process"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-5ff077">
                  How It Works
                </a>
              </li>
              
              <li data-pebble-id="pb-597c72">
                <a
                  href="#about"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-097af3">
                  About Dana
                </a>
              </li>
              
              <li data-pebble-id="pb-33feaf">
                <a
                  href="#pricing"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-dd57df">
                  Fees
                </a>
              </li>
              
              <li data-pebble-id="pb-ecc47b">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-97ee7e">
                  Contact
                </a>
              </li>
              
            </ul>
          </nav>

        </div>

        {/* Bottom row — divider + copyright */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-slate-600 text-xs" data-pebble-id="pb-27a598">
            &copy; 2025 Maple & Hart Law. All rights reserved.
          </p>
          <p className="text-slate-700 text-xs" data-pebble-id="pb-69772b">
            Licensed &amp; insured
          </p>
        </div>

      </div>
    </footer>
  );
}
