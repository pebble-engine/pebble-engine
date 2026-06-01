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
          <p className="text-amber-800 text-sm uppercase tracking-widest font-sans mb-3" data-pebble-id="pb-df2220">
            Tonight's plates
          </p>
          <h2 className="text-stone-900 font-serif text-4xl md:text-6xl leading-tight max-w-xl" data-pebble-id="pb-a18b2e">
            <RevealWords>Food made from what the ground gave us this week.</RevealWords>
          </h2>
        </div>

        {/* Menu items grid */}
        <Stagger className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
          
          <StaggerItem className="group flex flex-col">
            {/* Food photograph */}
            <div className="relative aspect-[4/3] rounded-2xl overflow-hidden mb-5">
              <Image
                src="https://images.pexels.com/photos/3649535/pexels-photo-3649535.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Roasted Beet & Whipped Chèvre"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>
            {/* Menu caption */}
            <div className="flex items-baseline justify-between mb-2">
              <h3 className="text-stone-900 font-serif text-xl leading-snug italic" data-pebble-id="pb-16d11d">
                Roasted Beet & Whipped Chèvre
              </h3>
              <span className="text-amber-800 font-sans text-sm font-semibold ml-4 flex-shrink-0" data-pebble-id="pb-311077">
                $16
              </span>
            </div>
            <p className="text-stone-900/65 font-sans text-base leading-relaxed" data-pebble-id="pb-268cfa">
              Chioggia beets from Holler Creek Farm, whipped local chèvre, toasted walnut, wildflower honey, torn herbs. Earthy, sweet, sharp.
            </p>
          </StaggerItem>
          
          <StaggerItem className="group flex flex-col">
            {/* Food photograph */}
            <div className="relative aspect-[4/3] rounded-2xl overflow-hidden mb-5">
              <Image
                src="https://images.pexels.com/photos/14537662/pexels-photo-14537662.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Smoked Duck Leg Confit"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>
            {/* Menu caption */}
            <div className="flex items-baseline justify-between mb-2">
              <h3 className="text-stone-900 font-serif text-xl leading-snug italic" data-pebble-id="pb-f8c65f">
                Smoked Duck Leg Confit
              </h3>
              <span className="text-amber-800 font-sans text-sm font-semibold ml-4 flex-shrink-0" data-pebble-id="pb-59574c">
                $38
              </span>
            </div>
            <p className="text-stone-900/65 font-sans text-base leading-relaxed" data-pebble-id="pb-01e3a7">
              Raised at Herondale Farm. Slow-rendered, crisped to order, served over creamy white polenta and braised Tuscan kale with pan jus.
            </p>
          </StaggerItem>
          
          <StaggerItem className="group flex flex-col">
            {/* Food photograph */}
            <div className="relative aspect-[4/3] rounded-2xl overflow-hidden mb-5">
              <Image
                src="https://images.pexels.com/photos/23340107/pexels-photo-23340107.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Sungold Tomato Pappardelle"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>
            {/* Menu caption */}
            <div className="flex items-baseline justify-between mb-2">
              <h3 className="text-stone-900 font-serif text-xl leading-snug italic" data-pebble-id="pb-caefaa">
                Sungold Tomato Pappardelle
              </h3>
              <span className="text-amber-800 font-sans text-sm font-semibold ml-4 flex-shrink-0" data-pebble-id="pb-e15bb0">
                $29
              </span>
            </div>
            <p className="text-stone-900/65 font-sans text-base leading-relaxed" data-pebble-id="pb-f19c61">
              Hand-rolled pasta, sungold tomatoes from Tivoli Farm, torn basil, aged pecorino, a thread of Calabrian chili oil. Summer in a bowl.
            </p>
          </StaggerItem>
          
          <StaggerItem className="group flex flex-col">
            {/* Food photograph */}
            <div className="relative aspect-[4/3] rounded-2xl overflow-hidden mb-5">
              <Image
                src="https://images.pexels.com/photos/14519322/pexels-photo-14519322.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Grilled Lamb Shoulder Chop"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>
            {/* Menu caption */}
            <div className="flex items-baseline justify-between mb-2">
              <h3 className="text-stone-900 font-serif text-xl leading-snug italic" data-pebble-id="pb-197631">
                Grilled Lamb Shoulder Chop
              </h3>
              <span className="text-amber-800 font-sans text-sm font-semibold ml-4 flex-shrink-0" data-pebble-id="pb-cc3d68">
                $42
              </span>
            </div>
            <p className="text-stone-900/65 font-sans text-base leading-relaxed" data-pebble-id="pb-3efa38">
              Hudson Valley pasture-raised lamb from Kinderhook Farm. Wood-fired, rested, plated with charred spring onions and salsa verde.
            </p>
          </StaggerItem>
          
          <StaggerItem className="group flex flex-col">
            {/* Food photograph */}
            <div className="relative aspect-[4/3] rounded-2xl overflow-hidden mb-5">
              <Image
                src="https://images.pexels.com/photos/29211866/pexels-photo-29211866.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Cornmeal Cake & Stone Fruit"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>
            {/* Menu caption */}
            <div className="flex items-baseline justify-between mb-2">
              <h3 className="text-stone-900 font-serif text-xl leading-snug italic" data-pebble-id="pb-5fa62e">
                Cornmeal Cake & Stone Fruit
              </h3>
              <span className="text-amber-800 font-sans text-sm font-semibold ml-4 flex-shrink-0" data-pebble-id="pb-72761e">
                $13
              </span>
            </div>
            <p className="text-stone-900/65 font-sans text-base leading-relaxed" data-pebble-id="pb-e75adf">
              Butter-rich cornmeal cake, roasted peaches from Barton Orchards, crème fraîche, a pinch of fleur de sel. Simple and unhurried.
            </p>
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
