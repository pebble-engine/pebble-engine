"use client";
import { motion } from "framer-motion";
import Image from "next/image";
import { GALLERY_IMAGES } from "@/content/site";

// Fallback Unsplash photos used until the customer drops their own files into
// /public/images/gallery/ and populates GALLERY_IMAGES.
const FALLBACK = [
  { src: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&w=900&q=70", alt: "Service technician at work" },
  { src: "https://images.unsplash.com/photo-1572883454114-1cf0031ede2a?auto=format&fit=crop&w=900&q=70", alt: "Suburban home exterior" },
  { src: "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?auto=format&fit=crop&w=900&q=70", alt: "Green lawn" },
  { src: "https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6?auto=format&fit=crop&w=900&q=70", alt: "Modern house front" },
  { src: "https://images.unsplash.com/photo-1604754742629-3e5728249d73?auto=format&fit=crop&w=900&q=70", alt: "Treated yard" },
  { src: "https://images.unsplash.com/photo-1597211833712-5e41faa202ea?auto=format&fit=crop&w=900&q=70", alt: "Spray treatment in progress" },
];

export function Gallery() {
  const images = GALLERY_IMAGES.length ? GALLERY_IMAGES : FALLBACK;
  if (!images.length) return null;

  return (
    <section id="gallery" className="relative py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
            Recent work
          </p>
          <h2 className="mt-3 font-display text-4xl font-bold tracking-tight text-fg sm:text-5xl">
            On-the-job
          </h2>
        </div>

        <div className="mt-12 grid grid-cols-2 gap-3 sm:grid-cols-3">
          {images.slice(0, 6).map((img, i) => (
            <motion.div
              key={img.src}
              initial={{ opacity: 0, scale: 0.96 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: i * 0.05, ease: "easeOut" }}
              className="group relative aspect-square overflow-hidden rounded-2xl border border-border"
            >
              <Image
                src={img.src}
                alt={img.alt}
                fill
                sizes="(min-width: 640px) 33vw, 50vw"
                className="object-cover transition-transform duration-500 group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-bg/30 via-transparent to-transparent" />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
