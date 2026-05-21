import * as React from "react";
import Image from "next/image";
import Link from "next/link";
import { cn } from "@/lib/cn";

type CategoryCardProps = {
  name: string;
  description: string;
  imageUrl: string;
  href: string;
  className?: string;
};

/**
 * CategoryCard — square photo tile with bottom gradient overlay,
 * italic Bodoni headline, and a tracked uppercase "Shop now ->" label.
 * Used in the 2x2 CategoryGrid on the homepage and the shop index.
 */
export function CategoryCard({
  name,
  description,
  imageUrl,
  href,
  className,
}: CategoryCardProps) {
  return (
    <Link
      href={href}
      className={cn(
        "group relative block aspect-square overflow-hidden rounded-2xl bg-surface-container shadow-vapor",
        "transition-transform duration-500 ease-out hover:-translate-y-1",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-4 focus-visible:ring-offset-surface",
        className,
      )}
    >
      <Image
        src={imageUrl}
        alt={name}
        fill
        sizes="(min-width: 1024px) 600px, (min-width: 768px) 50vw, 100vw"
        className="object-cover transition-transform duration-700 ease-out group-hover:scale-105"
      />
      {/* Bottom gradient overlay */}
      <div
        className="absolute inset-0 bg-gradient-to-t from-on-surface/75 via-on-surface/15 to-transparent"
        aria-hidden="true"
      />
      <div className="absolute inset-x-0 bottom-0 p-6 md:p-8 text-white">
        <h3 className="font-display italic text-3xl md:text-4xl leading-none mb-2">
          {name}
        </h3>
        <p className="text-sm md:text-base text-white/80 mb-4 max-w-sm leading-relaxed">
          {description}
        </p>
        <span className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-white">
          Shop now
          <span aria-hidden="true" className="transition-transform duration-300 group-hover:translate-x-1">
            &rarr;
          </span>
        </span>
      </div>
    </Link>
  );
}
