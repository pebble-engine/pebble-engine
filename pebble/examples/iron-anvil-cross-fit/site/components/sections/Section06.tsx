export default function FooterAnchoredBold() {
  return (
    <footer className="bg-zinc-900 border-t-2 border-zinc-50/10 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — brand + tagline left, nav right */}
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-8 mb-10">

          {/* Brand identity */}
          <div className="max-w-xs">
            <p className="text-zinc-50 text-base font-black uppercase tracking-widest leading-tight" data-pebble-id="pb-3102b6">
              Iron Anvil CrossFit
            </p>
            <p className="text-zinc-50/40 text-sm mt-2 leading-relaxed" data-pebble-id="pb-1b5bb9">
              Train hard. Show up. Ring the bell.
            </p>
          </div>

          {/* Nav links — caps, tight */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-3">
              
              <li data-pebble-id="pb-60f11e">
                <a
                  href="#services"
                  className="text-zinc-50/50 text-xs font-black uppercase tracking-[0.2em] hover:text-lime-400 transition" data-pebble-id="pb-dc10d3">
                  PROGRAMS
                </a>
              </li>
              
              <li data-pebble-id="pb-dfdd0f">
                <a
                  href="#pricing"
                  className="text-zinc-50/50 text-xs font-black uppercase tracking-[0.2em] hover:text-lime-400 transition" data-pebble-id="pb-7f50a6">
                  PRICING
                </a>
              </li>
              
              <li data-pebble-id="pb-d9ec81">
                <a
                  href="#about"
                  className="text-zinc-50/50 text-xs font-black uppercase tracking-[0.2em] hover:text-lime-400 transition" data-pebble-id="pb-a7b889">
                  OUR STORY
                </a>
              </li>
              
              <li data-pebble-id="pb-8d4850">
                <a
                  href="#about"
                  className="text-zinc-50/50 text-xs font-black uppercase tracking-[0.2em] hover:text-lime-400 transition" data-pebble-id="pb-80d6c9">
                  FIRST LIGHT CREW
                </a>
              </li>
              
              <li data-pebble-id="pb-f399e5">
                <a
                  href="#contact"
                  className="text-zinc-50/50 text-xs font-black uppercase tracking-[0.2em] hover:text-lime-400 transition" data-pebble-id="pb-cc9dc2">
                  CONTACT
                </a>
              </li>
              
            </ul>
          </nav>

        </div>

        {/* Bottom row — copyright with lime accent divider */}
        <div className="flex items-center gap-4">
          <div className="w-8 h-0.5 bg-lime-400" aria-hidden="true" />
          <p className="text-zinc-50/30 text-xs font-bold uppercase tracking-widest" data-pebble-id="pb-c48404">
            &copy; 2025 Iron Anvil CrossFit. All rights reserved.
          </p>
        </div>

      </div>
    </footer>
  );
}
