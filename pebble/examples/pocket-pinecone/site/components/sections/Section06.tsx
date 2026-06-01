export default function FooterPopPlayful() {
  return (
    <footer className="bg-purple-900 py-14 px-8">
      <div className="container mx-auto max-w-6xl">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-10">

          {/* Left — name + tagline */}
          <div className="flex-shrink-0 max-w-xs">
            <p className="text-white text-lg font-extrabold leading-snug" data-pebble-id="pb-41e186">
              Pocket & Pinecone
            </p>
            <p className="text-pink-300 text-sm mt-2 leading-relaxed" data-pebble-id="pb-c7b3c1">
              A little shop, hand-picked with love. Come wander in.
            </p>
          </div>

          {/* Middle — nav links */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-6 gap-y-3">
              
              <li data-pebble-id="pb-4a25f2">
                <a
                  href="#services"
                  className="text-purple-200 text-sm font-semibold hover:text-pink-400 hover:underline underline-offset-2 transition" data-pebble-id="pb-1e57c5">
                  What's in store
                </a>
              </li>
              
              <li data-pebble-id="pb-83b17b">
                <a
                  href="#about"
                  className="text-purple-200 text-sm font-semibold hover:text-pink-400 hover:underline underline-offset-2 transition" data-pebble-id="pb-02798b">
                  Our story
                </a>
              </li>
              
              <li data-pebble-id="pb-147c79">
                <a
                  href="#services"
                  className="text-purple-200 text-sm font-semibold hover:text-pink-400 hover:underline underline-offset-2 transition" data-pebble-id="pb-96a2a9">
                  Mystery cubby
                </a>
              </li>
              
              <li data-pebble-id="pb-a1c9e2">
                <a
                  href="#pricing"
                  className="text-purple-200 text-sm font-semibold hover:text-pink-400 hover:underline underline-offset-2 transition" data-pebble-id="pb-996e35">
                  Gift ideas
                </a>
              </li>
              
              <li data-pebble-id="pb-7cd742">
                <a
                  href="#contact"
                  className="text-purple-200 text-sm font-semibold hover:text-pink-400 hover:underline underline-offset-2 transition" data-pebble-id="pb-d40b5c">
                  Visit us
                </a>
              </li>
              
            </ul>
          </nav>

          {/* Right — copyright */}
          <div className="flex-shrink-0 text-purple-400 text-sm">
            &copy; 2025 Pocket & Pinecone. Made with joy.
          </div>

        </div>

        {/* Bottom accent strip */}
        <div aria-hidden="true" className="mt-10 h-1.5 rounded-full bg-gradient-to-r from-pink-500 via-amber-300 to-pink-500 opacity-60" />
      </div>
    </footer>
  );
}
