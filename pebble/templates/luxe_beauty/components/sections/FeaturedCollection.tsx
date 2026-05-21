import * as React from "react";
import { ProductCard } from "@/components/ui/ProductCard";
import { FEATURED_PRODUCTS } from "@/content/site";

/**
 * FeaturedCollection — horizontal-scrolling featured product row.
 * Returns null when FEATURED_PRODUCTS is empty (anti-slop: no invented inventory).
 */
export function FeaturedCollection() {
  if (FEATURED_PRODUCTS.length === 0) {
    return null;
  }

  return (
    <section
      aria-labelledby="featured-heading"
      className="bg-surface-container"
    >
      <div className="page-container py-section-mobile md:py-section-desktop">
        <div className="mb-10 md:mb-14 max-w-2xl">
          <p className="text-label mb-3">Featured</p>
          <h2 id="featured-heading" className="text-headline italic">
            From the shelf
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 md:gap-6">
          {FEATURED_PRODUCTS.map((product) => (
            <ProductCard
              key={product.id}
              name={product.name}
              category={product.category}
              price={product.price}
              imageUrl={product.image_url}
              href={product.href}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
