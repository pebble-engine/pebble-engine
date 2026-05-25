import { Reveal } from "@/components/ui/Reveal";
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
import { SERVICES } from "@/content/site";

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

export function Services() {
  return (
    <Reveal>
    <section className="py-24">
      <div className="max-w-6xl mx-auto px-8">
        <p className="text-[var(--color-accent)] text-xs font-bold uppercase tracking-[0.18em] mb-2">
          What we do
        </p>
        <h2 className="font-bold text-4xl text-[var(--color-text-primary)] mb-12">
          Services
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {SERVICES.map((svc) => {
            const Icon = ICON_MAP[svc.icon] ?? Wrench;
            return (
              <div
                key={svc.id}
                className="bg-[var(--color-surface-1)] border border-[var(--color-border)] rounded-2xl p-8"
              >
                <div className="w-14 h-14 rounded-full bg-[var(--color-accent)]/10 flex items-center justify-center mb-6">
                  <Icon className="w-6 h-6 text-[var(--color-accent)]" />
                </div>
                <h3 className="font-bold text-[22px] text-[var(--color-text-primary)] mb-2">
                  {svc.title}
                </h3>
                <p className="text-[15px] text-[var(--color-text-secondary)] leading-relaxed max-w-prose">
                  {svc.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
    </Reveal>
  );
}
