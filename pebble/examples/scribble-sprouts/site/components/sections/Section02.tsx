"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import Parallax from "@/components/motion/Parallax";

export default function AboutOriginPlayful() {
  return (
    <section className="bg-pink-50 py-24 px-8 overflow-hidden">
      <div className="container mx-auto max-w-6xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">

          {/* Portrait — left column with playful frame */}
          <div className="relative">
            <div className="relative aspect-[3/4] rounded-[2.5rem] overflow-hidden shadow-xl ring-4 ring-pink-300">
              <Parallax className="absolute inset-0" distance={30}>
                <Image
                  src="https://images.pexels.com/photos/8381934/pexels-photo-8381934.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="We built the studio we always wished existed for kids"
                  fill
                  priority
                  className="object-cover"
                />
              </Parallax>
            </div>
            {/* Floating accent blocks */}
            <div aria-hidden="true" className="absolute -bottom-6 -right-6 w-36 h-36 rounded-3xl bg-amber-300 -z-10" />
            <div aria-hidden="true" className="absolute -top-5 -left-5 w-20 h-20 rounded-2xl bg-pink-400 -z-10 rotate-6" />
          </div>

          {/* Prose — right column */}
          <div>
            <p className="inline-flex items-center gap-2 bg-pink-100 text-pink-600 text-sm font-bold px-5 py-2 rounded-full mb-6" data-pebble-id="pb-c75fbe">
              How Scribble Sprouts began 🌱
            </p>
            <h2 className="text-purple-900 text-5xl md:text-6xl font-extrabold leading-tight mb-8 max-w-lg" data-pebble-id="pb-ab2958">
              <RevealWords>We built the studio we always wished existed for kids</RevealWords>
            </h2>

            
            <p className="text-purple-900/70 text-xl leading-relaxed mb-6" data-pebble-id="pb-80dff8">
              Scribble Sprouts started because we kept seeing kids hesitate before picking up a brush — worried their art wasn't good enough. We wanted a place where that thought never even had a chance to form. So we opened our doors, splattered paint on the walls, and got to work.
            </p>
            
            <p className="text-purple-900/70 text-xl leading-relaxed mb-6" data-pebble-id="pb-784014">
              Every Saturday morning this room fills with kids ages 4 to 12, and the noise and color and laughter are absolutely wonderful. We do painting, clay, collage, and whatever glorious mess we can dream up together. The messier it gets, the better the art usually is.
            </p>
            
            <p className="text-purple-900/70 text-xl leading-relaxed mb-6" data-pebble-id="pb-311fb3">
              Our Wall of Fame is the heart of the studio. Before any artwork goes home, it goes up on the wall — every single piece, from every single kid. Nobody leaves without seeing their work celebrated. That's our promise, and it's the thing parents tell us matters most.
            </p>
            

            {/* Signature */}
            <div className="mt-10 pt-8 border-t-2 border-dashed border-pink-200">
              <p className="text-purple-900 text-base font-bold italic" data-pebble-id="pb-2f134f">
                — Jamie, Founder & Chief Mess Maker
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
