import * as React from "react";
import Image from "next/image";
import Link from "next/link";
import { cn } from "@/lib/cn";

type PropertyCardProps = {
  name: string;
  location: string;
  beds: string;
  baths: string;
  price: string;
  imageUrl: string;
  href: string;
  badge?: "Exclusive" | "New" | "Pending" | null;
  className?: string;
};

/**
 * PropertyCard — aspect-4/5 image with cinematic-img filter, bottom gradient
 * mask, optional vermilion badge in the top-right, and a meta block below
 * with the signature "5 BEDS // 6 BATHS" vermilion-divider markup + an
 * Unbounded price line.
 */
export function PropertyCard({
  name,
  location,
  beds,
  baths,
  price,
  imageUrl,
  href,
  badge,
  className,
}: PropertyCardProps) {
  return (
    <Link
      href={href}
      className={cn(
        "group property-card focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-4 focus-visible:ring-offset-bg",
        className,
      )}
    >
      <div className="relative aspect-[4/5] overflow-hidden bg-surface">
        <Image
          src={imageUrl}
          alt={name}
          fill
          sizes="(min-width: 1024px) 480px, (min-width: 768px) 50vw, 100vw"
          className="object-cover cinematic-img"
        />
        {/* Bottom gradient mask */}
        <div
          className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-bg via-bg/40 to-transparent"
          aria-hidden="true"
        />
        {badge && (
          <span className="absolute top-4 right-4 inline-flex items-center px-3 py-1 bg-accent text-fg text-[10px] uppercase font-semibold tracking-[0.18em] cinematic-radius">
            {badge}
          </span>
        )}
      </div>

      {/* Meta block */}
      <div className="p-5 md:p-6">
        <p className="text-eyebrow mb-2">{location}</p>
        <h3 className="text-title text-fg mb-4">{name}</h3>
        <p className="text-eyebrow mb-2">
          <span className="text-fg">{beds} BEDS</span>
          <span className="text-accent mx-2" aria-hidden="true">
            //
          </span>
          <span className="text-fg">{baths} BATHS</span>
        </p>
        <p className="font-display font-black text-2xl tracking-tighter text-fg">
          {price}
        </p>
      </div>
    </Link>
  );
}
