"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesPhotoGrid() {
  return (
    <section className="bg-slate-50 py-24 px-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-14 max-w-2xl">
          <p className="text-sky-700 text-xs font-semibold uppercase tracking-[0.2em] mb-4" data-pebble-id="pb-69fb4a">
            What We Offer
          </p>
          <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight tracking-tight" data-pebble-id="pb-8701d7">
            <RevealWords>Roofing Services Built for Kansas City Weather</RevealWords>
          </h2>
        </div>

        <Stagger className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          
          <StaggerItem className="flex flex-col rounded-2xl overflow-hidden border border-slate-200 bg-slate-50">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/37677476/pexels-photo-37677476.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Full Roof Replacement"
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-6 flex flex-col gap-3 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-b93b7c">
                Full Roof Replacement
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-3834f6">
                Complete tear-off and installation using certified materials — with manufacturer warranty eligibility on every job.
              </p>
            </div>
          </StaggerItem>
          
          <StaggerItem className="flex flex-col rounded-2xl overflow-hidden border border-slate-200 bg-slate-50">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/237907/pexels-photo-237907.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Storm Damage Repair"
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-6 flex flex-col gap-3 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-60c914">
                Storm Damage Repair
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-f96653">
                Hail, wind, and rain don't wait. We assess damage fast and get your roof protected before the next storm hits.
              </p>
            </div>
          </StaggerItem>
          
          <StaggerItem className="flex flex-col rounded-2xl overflow-hidden border border-slate-200 bg-slate-50">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/7190868/pexels-photo-7190868.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Insurance Claim Assistance"
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-6 flex flex-col gap-3 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-2c731a">
                Insurance Claim Assistance
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-ba5c6c">
                We work directly with your insurance adjuster so you get the full coverage you're entitled to — no guesswork.
              </p>
            </div>
          </StaggerItem>
          
          <StaggerItem className="flex flex-col rounded-2xl overflow-hidden border border-slate-200 bg-slate-50">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/8293635/pexels-photo-8293635.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Residential Inspections"
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-6 flex flex-col gap-3 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-aa131d">
                Residential Inspections
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-170d3c">
                A thorough written inspection report to give you clarity on your roof's condition, whether you're buying, selling, or just checking.
              </p>
            </div>
          </StaggerItem>
          
          <StaggerItem className="flex flex-col rounded-2xl overflow-hidden border border-slate-200 bg-slate-50">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/5667308/pexels-photo-5667308.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Gutter Installation & Cleaning"
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-6 flex flex-col gap-3 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-d0863b">
                Gutter Installation & Cleaning
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-3ca04a">
                Properly installed and clear gutters protect your foundation and extend the life of your new roof.
              </p>
            </div>
          </StaggerItem>
          
        </Stagger>
      </div>
    </section>
  );
}
