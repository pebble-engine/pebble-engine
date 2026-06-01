export default function FooterPopPlayful() {
  return (
    <footer className="bg-purple-900 py-14 px-8">
      <div className="container mx-auto max-w-6xl">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-10">

          {/* Left — name + tagline */}
          <div className="flex-shrink-0 max-w-xs">
            <p className="text-white text-lg font-extrabold leading-snug" data-pebble-id="pb-61042f">
              Scribble Sprouts
            </p>
            <p className="text-pink-300 text-sm mt-2 leading-relaxed" data-pebble-id="pb-9237ce">
              Making a glorious mess since day one. Every kid's a masterpiece. 🎨
            </p>
          </div>

          {/* Middle — nav links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-6 gap-y-3">
              
              <li data-pebble-id="pb-d3702c">
                <a
                  href="#services"
                  className="text-purple-200 text-sm font-semibold hover:text-pink-400 hover:underline underline-offset-2 transition" data-pebble-id="pb-f5d328">
                  Classes
                </a>
              </li>
              
              <li data-pebble-id="pb-a4722c">
                <a
                  href="#about"
                  className="text-purple-200 text-sm font-semibold hover:text-pink-400 hover:underline underline-offset-2 transition" data-pebble-id="pb-1ec25e">
                  Our Story
                </a>
              </li>
              
              <li data-pebble-id="pb-4f6ec1">
                <a
                  href="#gallery"
                  className="text-purple-200 text-sm font-semibold hover:text-pink-400 hover:underline underline-offset-2 transition" data-pebble-id="pb-8a2ea2">
                  Wall of Fame
                </a>
              </li>
              
              <li data-pebble-id="pb-a37603">
                <a
                  href="#pricing"
                  className="text-purple-200 text-sm font-semibold hover:text-pink-400 hover:underline underline-offset-2 transition" data-pebble-id="pb-580434">
                  Pricing
                </a>
              </li>
              
              <li data-pebble-id="pb-e90521">
                <a
                  href="#contact"
                  className="text-purple-200 text-sm font-semibold hover:text-pink-400 hover:underline underline-offset-2 transition" data-pebble-id="pb-51628e">
                  Contact
                </a>
              </li>
              
            </ul>
          </nav>

          {/* Right — copyright */}
          <div className="flex-shrink-0 text-purple-400 text-sm">
            &copy; 2025 Scribble Sprouts. Made with joy.
          </div>

        </div>

        {/* Bottom accent strip */}
        <div aria-hidden="true" className="mt-10 h-1.5 rounded-full bg-gradient-to-r from-pink-500 via-amber-300 to-pink-500 opacity-60" />
      </div>
    </footer>
  );
}
