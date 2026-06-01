"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesMenu() {
  return (
    <section className="bg-stone-50 py-32 px-8">
      <div className="container mx-auto max-w-5xl">

        {/* Section header — centered, airy */}
        <div className="text-center mb-20">
          <p className="text-amber-600 text-xs uppercase tracking-[0.25em] mb-5 font-light" data-pebble-id="pb-7c41f1">
            What we offer.
          </p>
          <h2 className="text-stone-700 text-5xl md:text-6xl font-light leading-tight max-w-xl mx-auto tracking-tight" data-pebble-id="pb-0e6458">
            <RevealWords>Treatments made to slow you down, not check you off.</RevealWords>
          </h2>
        </div>

        {/* Services — stacked menu rows with image thumbnails */}
        <Stagger className="divide-y divide-stone-200">
          
          <StaggerItem className="group flex items-center gap-8 py-10 hover:bg-stone-100/60 transition-colors duration-300 px-4 -mx-4 rounded-2xl">
            {/* Thumbnail */}
            <div className="relative flex-shrink-0 w-20 h-20 rounded-xl overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/19695967/pexels-photo-19695967.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="The Ritual Welcome"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>

            {/* Copy */}
            <div className="flex-1 min-w-0">
              <h3 className="text-stone-700 text-xl font-light leading-snug mb-1 tracking-tight" data-pebble-id="pb-421986">
                The Ritual Welcome
              </h3>
              <p className="text-stone-400 text-base font-light leading-relaxed truncate" data-pebble-id="pb-2ffab6">
                Every session begins here: warm basin foot soak, cedar-and-chamomile tea, and a few minutes of stillness before you reach the table.
              </p>
            </div>

            {/* Price */}
            <div className="flex-shrink-0 text-right">
              <span className="text-amber-600 text-base font-light tracking-wide" data-pebble-id="pb-9f72b8">
                Included in all
              </span>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group flex items-center gap-8 py-10 hover:bg-stone-100/60 transition-colors duration-300 px-4 -mx-4 rounded-2xl">
            {/* Thumbnail */}
            <div className="relative flex-shrink-0 w-20 h-20 rounded-xl overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/9146381/pexels-photo-9146381.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Deep Restore Massage"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>

            {/* Copy */}
            <div className="flex-1 min-w-0">
              <h3 className="text-stone-700 text-xl font-light leading-snug mb-1 tracking-tight" data-pebble-id="pb-63a287">
                Deep Restore Massage
              </h3>
              <p className="text-stone-400 text-base font-light leading-relaxed truncate" data-pebble-id="pb-aeda51">
                Slow, deliberate pressure along the back and shoulders. We work with your tension, not against it — an hour of release that stays with you.
              </p>
            </div>

            {/* Price */}
            <div className="flex-shrink-0 text-right">
              <span className="text-amber-600 text-base font-light tracking-wide" data-pebble-id="pb-bfacb3">
                From $120
              </span>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group flex items-center gap-8 py-10 hover:bg-stone-100/60 transition-colors duration-300 px-4 -mx-4 rounded-2xl">
            {/* Thumbnail */}
            <div className="relative flex-shrink-0 w-20 h-20 rounded-xl overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/6763615/pexels-photo-6763615.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Cedar & Clay Facial"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>

            {/* Copy */}
            <div className="flex-1 min-w-0">
              <h3 className="text-stone-700 text-xl font-light leading-snug mb-1 tracking-tight" data-pebble-id="pb-d839d4">
                Cedar & Clay Facial
              </h3>
              <p className="text-stone-400 text-base font-light leading-relaxed truncate" data-pebble-id="pb-620c35">
                A grounding facial using mineral-rich clay and cedar extract. Skin left clear and calm; nothing stripped, nothing inflamed.
              </p>
            </div>

            {/* Price */}
            <div className="flex-shrink-0 text-right">
              <span className="text-amber-600 text-base font-light tracking-wide" data-pebble-id="pb-ecf3ca">
                From $105
              </span>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group flex items-center gap-8 py-10 hover:bg-stone-100/60 transition-colors duration-300 px-4 -mx-4 rounded-2xl">
            {/* Thumbnail */}
            <div className="relative flex-shrink-0 w-20 h-20 rounded-xl overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/1926811/pexels-photo-1926811.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Couples' Sanctuary"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>

            {/* Copy */}
            <div className="flex-1 min-w-0">
              <h3 className="text-stone-700 text-xl font-light leading-snug mb-1 tracking-tight" data-pebble-id="pb-52bc85">
                Couples' Sanctuary
              </h3>
              <p className="text-stone-400 text-base font-light leading-relaxed truncate" data-pebble-id="pb-ae747f">
                Side-by-side treatment in our private suite — ideal for anniversaries. Begins with two foot rituals and teas, then a synchronized massage.
              </p>
            </div>

            {/* Price */}
            <div className="flex-shrink-0 text-right">
              <span className="text-amber-600 text-base font-light tracking-wide" data-pebble-id="pb-bece18">
                From $260
              </span>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group flex items-center gap-8 py-10 hover:bg-stone-100/60 transition-colors duration-300 px-4 -mx-4 rounded-2xl">
            {/* Thumbnail */}
            <div className="relative flex-shrink-0 w-20 h-20 rounded-xl overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/6663434/pexels-photo-6663434.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Restorative Body Wrap"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>

            {/* Copy */}
            <div className="flex-1 min-w-0">
              <h3 className="text-stone-700 text-xl font-light leading-snug mb-1 tracking-tight" data-pebble-id="pb-d1bb63">
                Restorative Body Wrap
              </h3>
              <p className="text-stone-400 text-base font-light leading-relaxed truncate" data-pebble-id="pb-8896dc">
                Warm herb-infused linen wraps cocoon the body while tension melts. Ends with a gentle scalp massage and cool botanical mist.
              </p>
            </div>

            {/* Price */}
            <div className="flex-shrink-0 text-right">
              <span className="text-amber-600 text-base font-light tracking-wide" data-pebble-id="pb-ba880b">
                From $135
              </span>
            </div>
          </StaggerItem>
          
        </Stagger>
      </div>
    </section>
  );
}
