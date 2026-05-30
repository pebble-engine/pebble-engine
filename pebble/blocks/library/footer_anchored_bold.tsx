export default function FooterAnchoredBold() {
  return (
    <footer className="bg-{{bg}} border-t-2 border-{{fg}}/10 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — brand + tagline left, nav right */}
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-8 mb-10">

          {/* Brand identity */}
          <div className="max-w-xs">
            <p className="text-{{fg}} text-base font-black uppercase tracking-widest leading-tight">
              {{business_name}}
            </p>
            <p className="text-{{fg}}/40 text-sm mt-2 leading-relaxed">
              {{tagline}}
            </p>
          </div>

          {/* Nav links — caps, tight */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-3">
              {/* {{links_list_start}} */}
              <li>
                <a
                  href="{{links[].href}}"
                  className="text-{{fg}}/50 text-xs font-black uppercase tracking-[0.2em] hover:text-{{accent}} transition"
                >
                  {{links[].label}}
                </a>
              </li>
              {/* {{links_list_end}} */}
            </ul>
          </nav>

        </div>

        {/* Bottom row — copyright with lime accent divider */}
        <div className="flex items-center gap-4">
          <div className="w-8 h-0.5 bg-{{accent}}" aria-hidden="true" />
          <p className="text-{{fg}}/30 text-xs font-bold uppercase tracking-widest">
            &copy; {{year}} {{business_name}}. All rights reserved.
          </p>
        </div>

      </div>
    </footer>
  );
}
