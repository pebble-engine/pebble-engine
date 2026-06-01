export default function FooterSignature() {
  return (
    <footer className="bg-stone-50 border-t border-stone-200 py-12 px-8">
      <div className="container mx-auto max-w-5xl">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-10">

          {/* Left — business name + tagline */}
          <div className="flex-shrink-0 max-w-xs">
            <p className="text-stone-700 text-sm font-light tracking-wide" data-pebble-id="pb-cc4afc">
              Maren & Vale
            </p>
            <p className="text-stone-400 text-xs font-light mt-2 leading-relaxed tracking-wide" data-pebble-id="pb-82ed86">
              Fine jewelry, hand-fabricated at the bench. Portland, Oregon.
            </p>
          </div>

          {/* Middle — nav links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-3">
              
              <li data-pebble-id="pb-0d2d6a">
                <a
                  href="#services"
                  className="text-stone-400 text-xs font-light uppercase tracking-[0.15em] hover:text-amber-600 transition-colors duration-200" data-pebble-id="pb-af7bd2">
                  Commissions
                </a>
              </li>
              
              <li data-pebble-id="pb-47e92d">
                <a
                  href="#process"
                  className="text-stone-400 text-xs font-light uppercase tracking-[0.15em] hover:text-amber-600 transition-colors duration-200" data-pebble-id="pb-f2f37b">
                  Process
                </a>
              </li>
              
              <li data-pebble-id="pb-59507f">
                <a
                  href="#about"
                  className="text-stone-400 text-xs font-light uppercase tracking-[0.15em] hover:text-amber-600 transition-colors duration-200" data-pebble-id="pb-b9a09b">
                  About
                </a>
              </li>
              
              <li data-pebble-id="pb-3fd89d">
                <a
                  href="#contact"
                  className="text-stone-400 text-xs font-light uppercase tracking-[0.15em] hover:text-amber-600 transition-colors duration-200" data-pebble-id="pb-701497">
                  Contact
                </a>
              </li>
              
            </ul>
          </nav>

          {/* Right — copyright */}
          <div className="flex-shrink-0 text-stone-300 text-xs font-light tracking-wide">
            &copy; 2025 Maren & Vale
          </div>

        </div>
      </div>
    </footer>
  );
}
