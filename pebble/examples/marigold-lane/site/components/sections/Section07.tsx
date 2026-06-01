export default function FooterSignature() {
  return (
    <footer className="bg-stone-50 border-t border-stone-200 py-12 px-8">
      <div className="container mx-auto max-w-5xl">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-10">

          {/* Left — business name + tagline */}
          <div className="flex-shrink-0 max-w-xs">
            <p className="text-stone-700 text-sm font-light tracking-wide" data-pebble-id="pb-9b28c8">
              Marigold Lane
            </p>
            <p className="text-stone-400 text-xs font-light mt-2 leading-relaxed tracking-wide" data-pebble-id="pb-6be5fc">
              A neighborhood salon where your hair is known and your time is not rushed.
            </p>
          </div>

          {/* Middle — nav links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-3">
              
              <li data-pebble-id="pb-b04181">
                <a
                  href="#services"
                  className="text-stone-400 text-xs font-light uppercase tracking-[0.15em] hover:text-amber-600 transition-colors duration-200" data-pebble-id="pb-9ddb1e">
                  Services
                </a>
              </li>
              
              <li data-pebble-id="pb-13d744">
                <a
                  href="#about"
                  className="text-stone-400 text-xs font-light uppercase tracking-[0.15em] hover:text-amber-600 transition-colors duration-200" data-pebble-id="pb-81af73">
                  About
                </a>
              </li>
              
              <li data-pebble-id="pb-db2d5f">
                <a
                  href="#process"
                  className="text-stone-400 text-xs font-light uppercase tracking-[0.15em] hover:text-amber-600 transition-colors duration-200" data-pebble-id="pb-1a357c">
                  Our Process
                </a>
              </li>
              
              <li data-pebble-id="pb-3f2204">
                <a
                  href="#contact"
                  className="text-stone-400 text-xs font-light uppercase tracking-[0.15em] hover:text-amber-600 transition-colors duration-200" data-pebble-id="pb-439fd0">
                  Book
                </a>
              </li>
              
            </ul>
          </nav>

          {/* Right — copyright */}
          <div className="flex-shrink-0 text-stone-300 text-xs font-light tracking-wide">
            &copy; 2025 Marigold Lane
          </div>

        </div>
      </div>
    </footer>
  );
}
