import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { CTABand } from "@/components/sections/CTABand";
import { SERVICES } from "@/content/site";
import {
  Wrench,
  Hammer,
  Truck,
  Droplets,
  Waves,
  Flame,
  Snowflake,
  Wind,
  Home,
  ChefHat,
  HardHat,
  Leaf,
  Sprout,
  TreePine,
  Scissors,
  Heart,
  type LucideIcon,
} from "lucide-react";

const ICON_MAP: Record<string, LucideIcon> = {
  Wrench,
  Hammer,
  Truck,
  Droplets,
  Waves,
  Flame,
  Snowflake,
  Wind,
  Home,
  ChefHat,
  HardHat,
  Leaf,
  Sprout,
  TreePine,
  Scissors,
  Heart,
};

export default function ServicesPage() {
  return (
    <>
      <Navbar />
      <main className="flex-1">
        <section className="py-24">
          <div className="max-w-5xl mx-auto px-8">
            <h1 className="font-bold text-[36px] text-[var(--color-text-primary)] mb-12">
              Our services
            </h1>

            <div className="flex flex-col gap-6">
              {SERVICES.map((svc) => {
                const Icon = ICON_MAP[svc.icon] ?? Wrench;
                return (
                  <div
                    key={svc.id}
                    className="flex items-start gap-6 bg-[var(--color-surface-1)] border border-[var(--color-border)] rounded-2xl p-8"
                  >
                    <div className="w-14 h-14 shrink-0 rounded-full bg-[var(--color-accent)]/10 flex items-center justify-center">
                      <Icon className="w-6 h-6 text-[var(--color-accent)]" />
                    </div>
                    <div>
                      <h2 className="font-bold text-[22px] text-[var(--color-text-primary)] mb-2">
                        {svc.title}
                      </h2>
                      <p className="text-[15px] text-[var(--color-text-secondary)] leading-relaxed max-w-prose">
                        {svc.description}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        <CTABand />
      </main>
      <Footer />
    </>
  );
}
