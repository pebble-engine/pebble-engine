export default function FooterSignature() {
  return (
    <footer className="bg-stone-50 border-t border-stone-200 py-12 px-8">
      <div className="container mx-auto max-w-5xl">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-10">

          {/* Left — business name + tagline */}
          <div className="flex-shrink-0 max-w-xs">
            <p className="text-stone-700 text-sm font-light tracking-wide" data-pebble-id="pb-aa3607">
              Marrow & Mist
            </p>
            <p className="text-stone-400 text-xs font-light mt-2 leading-relaxed tracking-wide" data-pebble-id="pb-446d8a">
              A day spa where every treatment begins with stillness.
            </p>
          </div>

          {/* Middle — nav links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-3">
              
              <li data-pebble-id="pb-bac00e">
                <a
                  href="#services"
                  className="text-stone-400 text-xs font-light uppercase tracking-[0.15em] hover:text-amber-600 transition-colors duration-200" data-pebble-id="pb-b834cf">
                  OFFERINGS
                </a>
              </li>
              
              <li data-pebble-id="pb-849867">
                <a
                  href="#about"
                  className="text-stone-400 text-xs font-light uppercase tracking-[0.15em] hover:text-amber-600 transition-colors duration-200" data-pebble-id="pb-c1d1b6">
                  OUR STORY
                </a>
              </li>
              
              <li data-pebble-id="pb-3a2ccd">
                <a
                  href="#process"
                  className="text-stone-400 text-xs font-light uppercase tracking-[0.15em] hover:text-amber-600 transition-colors duration-200" data-pebble-id="pb-6c45e5">
                  HOW IT WORKS
                </a>
              </li>
              
              <li data-pebble-id="pb-65d0ef">
                <a
                  href="#contact"
                  className="text-stone-400 text-xs font-light uppercase tracking-[0.15em] hover:text-amber-600 transition-colors duration-200" data-pebble-id="pb-9b52b2">
                  BOOK A VISIT
                </a>
              </li>
              
            </ul>
          </nav>

          {/* Right — copyright */}
          <div className="flex-shrink-0 text-stone-300 text-xs font-light tracking-wide">
            &copy; 2025 Marrow & Mist
          </div>

        </div>
      </div>
    </footer>
  );
}
