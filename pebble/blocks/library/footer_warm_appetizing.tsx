export default function FooterWarm() {
  return (
    <footer className="bg-{{bg}} border-t border-{{fg}}/10 py-12 px-8">
      <div className="container mx-auto max-w-6xl">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8">

          {/* Left — business name + warm tagline */}
          <div className="flex-shrink-0 max-w-xs">
            <p className="text-{{fg}} font-serif text-base leading-snug">
              {{business_name}}
            </p>
            <p className="text-{{fg}}/50 font-sans text-sm mt-1 leading-relaxed italic">
              {{tagline}}
            </p>
          </div>

          {/* Middle — nav links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-6 gap-y-2">
              {/* {{links_list_start}} */}
              <li>
                <a
                  href="{{links[].href}}"
                  className="text-{{fg}}/55 font-sans text-sm hover:text-{{accent}} transition"
                >
                  {{links[].label}}
                </a>
              </li>
              {/* {{links_list_end}} */}
            </ul>
          </nav>

          {/* Right — copyright */}
          <div className="flex-shrink-0 text-{{fg}}/35 font-sans text-sm">
            &copy; {{year}} {{business_name}}. All rights reserved.
          </div>

        </div>
      </div>
    </footer>
  );
}
