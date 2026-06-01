export default function FooterWarm() {
  return (
    <footer className="bg-stone-50 border-t border-stone-900/10 py-12 px-8">
      <div className="container mx-auto max-w-6xl">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8">

          {/* Left — business name + warm tagline */}
          <div className="flex-shrink-0 max-w-xs">
            <p className="text-stone-900 font-serif text-base leading-snug" data-pebble-id="pb-88a184">
              Ember & Oak Roasters
            </p>
            <p className="text-stone-900/50 font-sans text-sm mt-1 leading-relaxed italic" data-pebble-id="pb-c6ba95">
              Small-batch, single-origin. Roasted in-house. Every bag hand-dated.
            </p>
          </div>

          {/* Middle — nav links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-6 gap-y-2">
              
              <li data-pebble-id="pb-75740f">
                <a
                  href="#services"
                  className="text-stone-900/55 font-sans text-sm hover:text-amber-700 transition" data-pebble-id="pb-af99b9">
                  Shop Coffee
                </a>
              </li>
              
              <li data-pebble-id="pb-5938b3">
                <a
                  href="#about"
                  className="text-stone-900/55 font-sans text-sm hover:text-amber-700 transition" data-pebble-id="pb-92e1e2">
                  Our Story
                </a>
              </li>
              
              <li data-pebble-id="pb-56f018">
                <a
                  href="#pricing"
                  className="text-stone-900/55 font-sans text-sm hover:text-amber-700 transition" data-pebble-id="pb-96f3d2">
                  Subscriptions
                </a>
              </li>
              
              <li data-pebble-id="pb-836998">
                <a
                  href="#contact"
                  className="text-stone-900/55 font-sans text-sm hover:text-amber-700 transition" data-pebble-id="pb-9ab62e">
                  Visit the Café
                </a>
              </li>
              
              <li data-pebble-id="pb-365fd9">
                <a
                  href="#contact"
                  className="text-stone-900/55 font-sans text-sm hover:text-amber-700 transition" data-pebble-id="pb-f87e8c">
                  Wholesale
                </a>
              </li>
              
            </ul>
          </nav>

          {/* Right — copyright */}
          <div className="flex-shrink-0 text-stone-900/35 font-sans text-sm">
            &copy; 2025 Ember & Oak Roasters. All rights reserved.
          </div>

        </div>
      </div>
    </footer>
  );
}
