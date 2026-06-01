export default function FooterWarm() {
  return (
    <footer className="bg-stone-50 border-t border-stone-900/10 py-12 px-8">
      <div className="container mx-auto max-w-6xl">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8">

          {/* Left — business name + warm tagline */}
          <div className="flex-shrink-0 max-w-xs">
            <p className="text-stone-900 font-serif text-base leading-snug" data-pebble-id="pb-a19ac3">
              Flour & Fern
            </p>
            <p className="text-stone-900/50 font-sans text-sm mt-1 leading-relaxed italic" data-pebble-id="pb-3d5cec">
              Small-batch sourdough baked slow, sold by noon.
            </p>
          </div>

          {/* Middle — nav links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-6 gap-y-2">
              
              <li data-pebble-id="pb-4c5304">
                <a
                  href="#services"
                  className="text-stone-900/55 font-sans text-sm hover:text-amber-700 transition" data-pebble-id="pb-939904">
                  What we bake
                </a>
              </li>
              
              <li data-pebble-id="pb-600f47">
                <a
                  href="#about"
                  className="text-stone-900/55 font-sans text-sm hover:text-amber-700 transition" data-pebble-id="pb-2bf30b">
                  Our story
                </a>
              </li>
              
              <li data-pebble-id="pb-218176">
                <a
                  href="#process"
                  className="text-stone-900/55 font-sans text-sm hover:text-amber-700 transition" data-pebble-id="pb-8a7e6b">
                  How it's made
                </a>
              </li>
              
              <li data-pebble-id="pb-8d7bf8">
                <a
                  href="#contact"
                  className="text-stone-900/55 font-sans text-sm hover:text-amber-700 transition" data-pebble-id="pb-6e754e">
                  Visit us
                </a>
              </li>
              
            </ul>
          </nav>

          {/* Right — copyright */}
          <div className="flex-shrink-0 text-stone-900/35 font-sans text-sm">
            &copy; 2025 Flour & Fern. All rights reserved.
          </div>

        </div>
      </div>
    </footer>
  );
}
