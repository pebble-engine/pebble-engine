import type { Metadata } from "next";
import { CategoryCard } from "@/components/ui/CategoryCard";
import { ProductCard } from "@/components/ui/ProductCard";
import { ScriptText } from "@/components/ui/ScriptText";
import {
  PRODUCT_CATEGORIES,
  FEATURED_PRODUCTS,
  SHOP_EYEBROW,
  SHOP_HEADLINE,
  SHOP_INTRO,
  SITE_TITLE,
} from "@/content/site";

export const metadata: Metadata = {
  title: `Shop | ${SITE_TITLE}`,
};

export default function ShopPage() {
  return (
    <>
      <section className="ethereal-bg">
        <div className="page-container pt-20 md:pt-32 pb-12 md:pb-16">
          <div className="max-w-2xl">
            <p className="text-label mb-4">{SHOP_EYEBROW}</p>
            <h1 className="text-display italic mb-2">{SHOP_HEADLINE}</h1>
            <ScriptText className="text-3xl md:text-4xl block mb-6">
              browse the atelier
            </ScriptText>
            <p className="text-body-lg max-w-xl">{SHOP_INTRO}</p>
          </div>
        </div>
      </section>

      {/* Category tiles */}
      <section aria-labelledby="categories-heading" className="bg-surface">
        <div className="page-container py-section-mobile md:py-section-desktop">
          <h2 id="categories-heading" className="text-label mb-8">
            Categories
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 md:gap-6">
            {PRODUCT_CATEGORIES.map((cat) => (
              <CategoryCard
                key={cat.id}
                name={cat.name}
                description={cat.description}
                imageUrl={cat.image_url}
                href={cat.href}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Featured grid — only renders when populated */}
      {FEATURED_PRODUCTS.length > 0 && (
        <section aria-labelledby="featured-products-heading" className="bg-surface-container">
          <div className="page-container py-section-mobile md:py-section-desktop">
            <h2 id="featured-products-heading" className="text-label mb-8">
              Featured products
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 md:gap-6">
              {FEATURED_PRODUCTS.map((p) => (
                <ProductCard
                  key={p.id}
                  name={p.name}
                  category={p.category}
                  price={p.price}
                  imageUrl={p.image_url}
                  href={p.href}
                />
              ))}
            </div>
          </div>
        </section>
      )}
    </>
  );
}
