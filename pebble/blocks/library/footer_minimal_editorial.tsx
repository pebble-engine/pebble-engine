export default function FooterMinimalEditorial() {
  return (
    <footer className="bg-{{bg}} border-t border-{{fg}}/8 py-12 px-8">
      <div className="container mx-auto max-w-5xl">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-8">

          {/* Left — name + tagline */}
          <div>
            <p className="font-serif text-{{fg}} text-base leading-snug">
              {{business_name}}
            </p>
            <p className="text-{{fg}}/35 text-xs font-sans mt-1 leading-relaxed max-w-xs">
              {{tagline}}
            </p>
          </div>

          {/* Center — sparse nav */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-2">
              {/* {{links_list_start}} */}
              <li>
                <a
                  href="{{links[].href}}"
                  className="text-{{fg}}/40 text-xs font-sans tracking-wide hover:text-{{fg}}/70 transition-colors"
                >
                  {{links[].label}}
                </a>
              </li>
              {/* {{links_list_end}} */}
            </ul>
          </nav>

          {/* Right — copyright, minimal */}
          <p className="text-{{fg}}/25 text-xs font-sans flex-shrink-0">
            &copy; {{year}}
          </p>

        </div>
      </div>
    </footer>
  );
}
