export default function FooterSignature() {
  return (
    <footer className="bg-stone-50 border-t border-stone-200 py-12 px-8">
      <div className="container mx-auto max-w-5xl">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-10">

          {/* Left — business name + tagline */}
          <div className="flex-shrink-0 max-w-xs">
            <p className="text-stone-700 text-sm font-light tracking-wide">
              {{business_name}}
            </p>
            <p className="text-stone-400 text-xs font-light mt-2 leading-relaxed tracking-wide">
              {{tagline}}
            </p>
          </div>

          {/* Middle — nav links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-3">
              {/* {{links_list_start}} */}
              <li>
                <a
                  href="{{links[].href}}"
                  className="text-stone-400 text-xs font-light uppercase tracking-[0.15em] hover:text-amber-600 transition-colors duration-200"
                >
                  {{links[].label}}
                </a>
              </li>
              {/* {{links_list_end}} */}
            </ul>
          </nav>

          {/* Right — copyright */}
          <div className="flex-shrink-0 text-stone-300 text-xs font-light tracking-wide">
            &copy; {{year}} {{business_name}}
          </div>

        </div>
      </div>
    </footer>
  );
}
