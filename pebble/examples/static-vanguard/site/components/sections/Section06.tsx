export default function FooterAnchoredBold() {
  return (
    <footer className="bg-zinc-900 border-t-2 border-zinc-50/10 py-12 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top row — brand + tagline left, nav right */}
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-8 mb-10">

          {/* Brand identity */}
          <div className="max-w-xs">
            <p className="text-zinc-50 text-base font-black uppercase tracking-widest leading-tight" data-pebble-id="pb-afe595">
              Static Vanguard
            </p>
            <p className="text-zinc-50/40 text-sm mt-2 leading-relaxed" data-pebble-id="pb-2e491a">
              Compete loud. Glitch first. Leave a signal.
            </p>
          </div>

          {/* Nav links — caps, tight */}
          <nav aria-label="Footer navigation">
            <ul className="flex flex-wrap gap-x-8 gap-y-3">
              
              <li data-pebble-id="pb-ef9faf">
                <a
                  href="#roster"
                  className="text-zinc-50/50 text-xs font-black uppercase tracking-[0.2em] hover:text-lime-400 transition" data-pebble-id="pb-becaf8">
                  ROSTER
                </a>
              </li>
              
              <li data-pebble-id="pb-7ed5c9">
                <a
                  href="#schedule"
                  className="text-zinc-50/50 text-xs font-black uppercase tracking-[0.2em] hover:text-lime-400 transition" data-pebble-id="pb-6557bd">
                  SCHEDULE
                </a>
              </li>
              
              <li data-pebble-id="pb-4cceaf">
                <a
                  href="#clips"
                  className="text-zinc-50/50 text-xs font-black uppercase tracking-[0.2em] hover:text-lime-400 transition" data-pebble-id="pb-08f1ba">
                  CLIPS
                </a>
              </li>
              
              <li data-pebble-id="pb-842500">
                <a
                  href="#partners"
                  className="text-zinc-50/50 text-xs font-black uppercase tracking-[0.2em] hover:text-lime-400 transition" data-pebble-id="pb-65f39e">
                  PARTNERS
                </a>
              </li>
              
              <li data-pebble-id="pb-06d8d2">
                <a
                  href="#contact"
                  className="text-zinc-50/50 text-xs font-black uppercase tracking-[0.2em] hover:text-lime-400 transition" data-pebble-id="pb-40b9ba">
                  CONTACT
                </a>
              </li>
              
            </ul>
          </nav>

        </div>

        {/* Bottom row — copyright with lime accent divider */}
        <div className="flex items-center gap-4">
          <div className="w-8 h-0.5 bg-lime-400" aria-hidden="true" />
          <p className="text-zinc-50/30 text-xs font-bold uppercase tracking-widest" data-pebble-id="pb-43f3a2">
            &copy; 2025 Static Vanguard. All rights reserved.
          </p>
        </div>

      </div>
    </footer>
  );
}
