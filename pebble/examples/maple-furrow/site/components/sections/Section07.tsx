export default function FooterWarm() {
  return (
    <footer className="bg-stone-50 border-t border-stone-900/10 py-12 px-8">
      <div className="container mx-auto max-w-6xl">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8">

          {/* Left — business name + warm tagline */}
          <div className="flex-shrink-0 max-w-xs">
            <p className="text-stone-900 font-serif text-base leading-snug" data-pebble-id="pb-2cdd76">
              Maple & Furrow
            </p>
            <p className="text-stone-900/50 font-sans text-sm mt-1 leading-relaxed italic" data-pebble-id="pb-4db666">
              Seasonal farm-to-table dining in the Hudson Valley. Named farms, real seasons, one unhurried meal.
            </p>
          </div>

          {/* Middle — nav links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-6 gap-y-2">
              
              <li data-pebble-id="pb-2bc47c">
                <a
                  href="#menu"
                  className="text-stone-900/55 font-sans text-sm hover:text-amber-800 transition" data-pebble-id="pb-84581c">
                  Menu
                </a>
              </li>
              
              <li data-pebble-id="pb-a880a3">
                <a
                  href="#contact"
                  className="text-stone-900/55 font-sans text-sm hover:text-amber-800 transition" data-pebble-id="pb-53c389">
                  Reservations
                </a>
              </li>
              
              <li data-pebble-id="pb-4dd5db">
                <a
                  href="#about"
                  className="text-stone-900/55 font-sans text-sm hover:text-amber-800 transition" data-pebble-id="pb-5caabd">
                  Our Story
                </a>
              </li>
              
              <li data-pebble-id="pb-7addde">
                <a
                  href="#pricing"
                  className="text-stone-900/55 font-sans text-sm hover:text-amber-800 transition" data-pebble-id="pb-51a6e0">
                  Private Dining
                </a>
              </li>
              
              <li data-pebble-id="pb-2a4c70">
                <a
                  href="#gallery"
                  className="text-stone-900/55 font-sans text-sm hover:text-amber-800 transition" data-pebble-id="pb-a2c96e">
                  Gallery
                </a>
              </li>
              
            </ul>
          </nav>

          {/* Right — copyright */}
          <div className="flex-shrink-0 text-stone-900/35 font-sans text-sm">
            &copy; 2025 Maple & Furrow. All rights reserved.
          </div>

        </div>
      </div>
    </footer>
  );
}
