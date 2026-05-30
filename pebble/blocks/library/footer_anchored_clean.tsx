export default function FooterAnchoredClean() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — name + links */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8 mb-10">

          {/* Business identity */}
          <div className="flex-shrink-0">
            <p className="text-slate-100 text-sm font-semibold tracking-wide">
              {{business_name}}
            </p>
            <p className="text-slate-500 text-xs mt-1 leading-relaxed max-w-xs">
              {{tagline}}
            </p>
          </div>

          {/* Navigation links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              {/* {{links_list_start}} */}
              <li>
                <a
                  href="{{links[].href}}"
                  className="text-slate-400 text-sm hover:text-slate-100 transition"
                >
                  {{links[].label}}
                </a>
              </li>
              {/* {{links_list_end}} */}
            </ul>
          </nav>

        </div>

        {/* Bottom row — divider + copyright */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-slate-600 text-xs">
            &copy; {{year}} {{business_name}}. All rights reserved.
          </p>
          <p className="text-slate-700 text-xs">
            Licensed &amp; insured
          </p>
        </div>

      </div>
    </footer>
  );
}
