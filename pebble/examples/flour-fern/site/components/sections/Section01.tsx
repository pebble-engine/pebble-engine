"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function MenuGrid() {
  return (
    <section className="bg-stone-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="mb-16">
          <p className="text-amber-700 text-sm uppercase tracking-widest font-sans mb-3" data-pebble-id="pb-fa2a39">
            What we're baking
          </p>
          <h2 className="text-stone-900 font-serif text-4xl md:text-6xl leading-tight max-w-xl" data-pebble-id="pb-0589bd">
            <RevealWords>Every loaf has somewhere to be by noon.</RevealWords>
          </h2>
        </div>

        {/* Menu items grid */}
        <Stagger className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
          
          <StaggerItem className="group flex flex-col">
            {/* Food photograph */}
            <div className="relative aspect-[4/3] rounded-2xl overflow-hidden mb-5">
              <Image
                src="https://images.pexels.com/photos/30632205/pexels-photo-30632205.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Country Sourdough"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>
            {/* Menu caption */}
            <div className="flex items-baseline justify-between mb-2">
              <h3 className="text-stone-900 font-serif text-xl leading-snug italic" data-pebble-id="pb-8ef6e8">
                Country Sourdough
              </h3>
              <span className="text-amber-700 font-sans text-sm font-semibold ml-4 flex-shrink-0" data-pebble-id="pb-05ec3c">
                $9
              </span>
            </div>
            <p className="text-stone-900/65 font-sans text-base leading-relaxed" data-pebble-id="pb-5f916d">
              Our everyday loaf — open crumb, crackly crust, two-day cold ferment. Made with local stone-milled flour and our house starter.
            </p>
          </StaggerItem>
          
          <StaggerItem className="group flex flex-col">
            {/* Food photograph */}
            <div className="relative aspect-[4/3] rounded-2xl overflow-hidden mb-5">
              <Image
                src="https://images.pexels.com/photos/14520462/pexels-photo-14520462.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Saturday Rye & Fig"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>
            {/* Menu caption */}
            <div className="flex items-baseline justify-between mb-2">
              <h3 className="text-stone-900 font-serif text-xl leading-snug italic" data-pebble-id="pb-fee9bb">
                Saturday Rye & Fig
              </h3>
              <span className="text-amber-700 font-sans text-sm font-semibold ml-4 flex-shrink-0" data-pebble-id="pb-dfe7de">
                $13
              </span>
            </div>
            <p className="text-stone-900/65 font-sans text-base leading-relaxed" data-pebble-id="pb-e935b9">
              Our most-asked-about loaf. Dark rye, dried fig, and a thirty-year-old starter inherited from our baker's grandmother. Available Saturdays only.
            </p>
          </StaggerItem>
          
          <StaggerItem className="group flex flex-col">
            {/* Food photograph */}
            <div className="relative aspect-[4/3] rounded-2xl overflow-hidden mb-5">
              <Image
                src="https://images.pexels.com/photos/6202224/pexels-photo-6202224.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Butter Croissant"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>
            {/* Menu caption */}
            <div className="flex items-baseline justify-between mb-2">
              <h3 className="text-stone-900 font-serif text-xl leading-snug italic" data-pebble-id="pb-a75ed8">
                Butter Croissant
              </h3>
              <span className="text-amber-700 font-sans text-sm font-semibold ml-4 flex-shrink-0" data-pebble-id="pb-b8fda9">
                $5
              </span>
            </div>
            <p className="text-stone-900/65 font-sans text-base leading-relaxed" data-pebble-id="pb-953fed">
              Laminated by hand each morning. Honey-lacquered, shatteringly flaky, with a soft, pillowy interior. Limited to 24 per day.
            </p>
          </StaggerItem>
          
          <StaggerItem className="group flex flex-col">
            {/* Food photograph */}
            <div className="relative aspect-[4/3] rounded-2xl overflow-hidden mb-5">
              <Image
                src="https://images.pexels.com/photos/15649849/pexels-photo-15649849.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Whole Wheat Sesame"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>
            {/* Menu caption */}
            <div className="flex items-baseline justify-between mb-2">
              <h3 className="text-stone-900 font-serif text-xl leading-snug italic" data-pebble-id="pb-798e41">
                Whole Wheat Sesame
              </h3>
              <span className="text-amber-700 font-sans text-sm font-semibold ml-4 flex-shrink-0" data-pebble-id="pb-b37830">
                $10
              </span>
            </div>
            <p className="text-stone-900/65 font-sans text-base leading-relaxed" data-pebble-id="pb-4aaa71">
              Nutty and substantial — 40% whole wheat, toasted sesame crust, slightly sweet crumb. Great for toast, better straight from the bag.
            </p>
          </StaggerItem>
          
          <StaggerItem className="group flex flex-col">
            {/* Food photograph */}
            <div className="relative aspect-[4/3] rounded-2xl overflow-hidden mb-5">
              <Image
                src="https://images.pexels.com/photos/30667454/pexels-photo-30667454.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Morning Pastry Box"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>
            {/* Menu caption */}
            <div className="flex items-baseline justify-between mb-2">
              <h3 className="text-stone-900 font-serif text-xl leading-snug italic" data-pebble-id="pb-9bef6d">
                Morning Pastry Box
              </h3>
              <span className="text-amber-700 font-sans text-sm font-semibold ml-4 flex-shrink-0" data-pebble-id="pb-b9ba9a">
                $22
              </span>
            </div>
            <p className="text-stone-900/65 font-sans text-base leading-relaxed" data-pebble-id="pb-dbf771">
              A rotating mix of what came out of the oven that morning — croissants, kouign-amann, cardamom buns. No two boxes are exactly alike.
            </p>
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
