import * as React from "react";
import Image from "next/image";
import { cn } from "@/lib/cn";

type MenuCardProps = {
  name: string;
  description: string;
  price: string;
  category: string;
  imageUrl: string;
  className?: string;
};

/**
 * MenuCard — rounded-3xl photo tile with bottom info block.
 * The "food is the product" trattoria layout — photo dominates, name and price
 * sit just below with a small category chip. Used in the masonry menu grid
 * on the homepage and the full /menu page.
 */
export function MenuCard({
  name,
  description,
  price,
  category,
  imageUrl,
  className,
}: MenuCardProps) {
  return (
    <article
      className={cn(
        "group relative block overflow-hidden rounded-3xl bg-surface warm-shadow",
        "transition-transform duration-500 ease-out hover:-translate-y-1",
        className,
      )}
    >
      <div className="relative aspect-[4/5] overflow-hidden bg-cream-alt">
        <Image
          src={imageUrl}
          alt={name}
          fill
          sizes="(min-width: 1024px) 380px, (min-width: 640px) 50vw, 100vw"
          className="object-cover transition-transform duration-700 ease-out group-hover:scale-105"
        />
        <span className="absolute left-4 top-4 inline-flex items-center rounded-full bg-cream/90 px-3 py-1 text-[10px] uppercase tracking-[0.18em] text-ink shadow-glass">
          {category}
        </span>
      </div>
      <div className="p-5 md:p-6">
        <div className="flex items-baseline justify-between gap-3 mb-2">
          <h3 className="font-display text-xl md:text-2xl leading-tight text-ink">
            {name}
          </h3>
          <span className="font-display text-lg text-crust">{price}</span>
        </div>
        <p className="text-sm text-ink-soft leading-relaxed">{description}</p>
      </div>
    </article>
  );
}
