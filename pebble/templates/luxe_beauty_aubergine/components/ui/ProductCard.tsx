import * as React from "react";
import Image from "next/image";
import Link from "next/link";
import { cn } from "@/lib/cn";

type ProductCardProps = {
  name: string;
  category: string;
  price: string;
  imageUrl: string;
  href: string;
  className?: string;
};

/**
 * ProductCard — glass card with image-top, info-bottom. Used in the
 * FeaturedCollection carousel and the shop grid.
 */
export function ProductCard({
  name,
  category,
  price,
  imageUrl,
  href,
  className,
}: ProductCardProps) {
  return (
    <Link
      href={href}
      className={cn(
        "group block rounded-2xl overflow-hidden glass-card transition-all duration-300 hover:-translate-y-1 hover:shadow-vapor",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-4 focus-visible:ring-offset-surface",
        className,
      )}
    >
      <div className="relative aspect-[4/5] bg-surface-container-low overflow-hidden">
        <Image
          src={imageUrl}
          alt={name}
          fill
          sizes="(min-width: 1024px) 320px, (min-width: 768px) 33vw, 100vw"
          className="object-cover transition-transform duration-700 ease-out group-hover:scale-105"
        />
      </div>
      <div className="p-5">
        <p className="text-label mb-1">{category}</p>
        <h3 className="font-display italic text-xl md:text-2xl leading-tight text-on-surface mb-2">
          {name}
        </h3>
        <p className="font-body text-sm text-on-surface-variant">{price}</p>
      </div>
    </Link>
  );
}
