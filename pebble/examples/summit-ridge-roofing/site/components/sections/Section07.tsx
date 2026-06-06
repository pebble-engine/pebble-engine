export default function FooterAnchoredClean() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — name + links */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8 mb-10">

          {/* Business identity */}
          <div className="flex-shrink-0">
            <p className="text-slate-100 text-sm font-semibold tracking-wide" data-pebble-id="pb-7811f7">
              Summit Ridge Roofing
            </p>
            <p className="text-slate-500 text-xs mt-1 leading-relaxed max-w-xs" data-pebble-id="pb-a5597f">
              Licensed roofing contractor serving Kansas City, MO — storm damage repair, full replacements, and insurance claim assistance.
            </p>
          </div>

          {/* Navigation links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              
              <li data-pebble-id="pb-0256c6">
                <a
                  href="#services"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-c82a89">
                  Services
                </a>
              </li>
              
              <li data-pebble-id="pb-531cdd">
                <a
                  href="#about"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-e1ef8a">
                  About
                </a>
              </li>
              
              <li data-pebble-id="pb-8e835e">
                <a
                  href="#coverage"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-ac7b18">
                  Service Area
                </a>
              </li>
              
              <li data-pebble-id="pb-d19b9b">
                <a
                  href="#contact"
                  className="text-slate-400 text-sm hover:text-slate-100 transition" data-pebble-id="pb-e72cbd">
                  Contact
                </a>
              </li>
              
            </ul>
          </nav>

        </div>

        {/* Bottom row — divider + copyright */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-slate-600 text-xs" data-pebble-id="pb-f391c3">
            &copy; 2025 Summit Ridge Roofing. All rights reserved.
          </p>
          <p className="text-slate-700 text-xs" data-pebble-id="pb-aefc88">
            Licensed &amp; insured
          </p>
        </div>

      </div>
    </footer>
  );
}
