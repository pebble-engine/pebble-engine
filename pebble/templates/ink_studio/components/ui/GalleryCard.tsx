import * as React from "react";
import Image from "next/image";
import { cn } from "@/lib/cn";

type GalleryCardProps = {
  title: string;
  style: string;
  imageUrl: string;
  alt: string;
  highlighted?: boolean;
  className?: string;
};

/**
 * GalleryCard — square portrait tile for the gallery + carousel.
 * When `highlighted`, renders the gold-border-glow + corner brackets
 * (DNA carousel center-image treatment).
 */
export function GalleryCard({
  title,
  style,
  imageUrl,
  alt,
  highlighted = false,
  className,
}: GalleryCardProps) {
  return (
    <figure
      className={cn(
        "group relative aspect-[3/4] overflow-hidden bg-ink-card",
        highlighted ? "corner-brackets gold-border-glow" : "border border-ink-border",
        className,
      )}
    >
      <Image
        src={imageUrl}
        alt={alt}
        fill
        sizes="(min-width: 1024px) 400px, (min-width: 768px) 50vw, 100vw"
        className="object-cover transition-transform duration-700 ease-out group-hover:scale-105"
      />
      <div
        className="absolute inset-0 bg-gradient-to-t from-ink-bg/90 via-ink-bg/10 to-transparent"
        aria-hidden="true"
      />
      <figcaption className="absolute inset-x-0 bottom-0 p-5 md:p-6 text-ink-fg">
        <p className="text-eyebrow mb-1">{style}</p>
        <h3 className="font-display text-2xl md:text-3xl leading-none">
          {title}
        </h3>
      </figcaption>
    </figure>
  );
}
