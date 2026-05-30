export default function FooterPopPlayful() {
  return (
    <footer className="bg-purple-900 py-14 px-8">
      <div className="container mx-auto max-w-6xl">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-10">

          {/* Left — name + tagline */}
          <div className="flex-shrink-0 max-w-xs">
            <p className="text-white text-lg font-extrabold leading-snug">
              {{business_name}}
            </p>
            <p className="text-pink-300 text-sm mt-2 leading-relaxed">
              {{tagline}}
            </p>
          </div>

          {/* Middle — nav links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-6 gap-y-3">
              {/* {{links_list_start}} */}
              <li>
                <a
                  href="{{links[].href}}"
                  className="text-purple-200 text-sm font-semibold hover:text-pink-400 hover:underline underline-offset-2 transition"
                >
                  {{links[].label}}
                </a>
              </li>
              {/* {{links_list_end}} */}
            </ul>
          </nav>

          {/* Right — copyright */}
          <div className="flex-shrink-0 text-purple-400 text-sm">
            &copy; {{year}} {{business_name}}. Made with joy.
          </div>

        </div>

        {/* Bottom accent strip */}
        <div aria-hidden="true" className="mt-10 h-1.5 rounded-full bg-gradient-to-r from-pink-500 via-amber-300 to-pink-500 opacity-60" />
      </div>
    </footer>
  );
}
