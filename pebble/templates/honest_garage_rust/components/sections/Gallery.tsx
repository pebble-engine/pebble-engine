"use client";
import { motion } from "framer-motion";
import Image from "next/image";
import { RefCode } from "@/components/ui/RefCode";
import { ImgRefTag } from "@/components/ui/ImgRefTag";
import { GALLERY_IMAGES } from "@/content/site";

// Fallback Unsplash photos used until the customer drops their own files into
// /public/images/gallery/ and populates GALLERY_IMAGES. Industrial / shop /
// vehicle photography selected to match the auto_honest_diag DNA.
const FALLBACK: { src: string; alt: string; ref: string }[] = [
  {
    src: "https://images.unsplash.com/photo-1486754735734-325b5831c3ad?auto=format&fit=crop&w=900&q=70",
    alt: "Engine bay close-up",
    ref: "IMG-REF-07001",
  },
  {
    src: "https://images.unsplash.com/photo-1632823471565-1ecdf7a6f5d6?auto=format&fit=crop&w=900&q=70",
    alt: "Brake assembly on the lift",
    ref: "IMG-REF-07014",
  },
  {
    src: "https://images.unsplash.com/photo-1487754180451-c456f719a1fc?auto=format&fit=crop&w=900&q=70",
    alt: "Tools on a workbench",
    ref: "IMG-REF-07022",
  },
  {
    src: "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=900&q=70",
    alt: "Tire mount-and-balance bay",
    ref: "IMG-REF-07033",
  },
  {
    src: "https://images.unsplash.com/photo-1486006920555-c77dcf18193c?auto=format&fit=crop&w=900&q=70",
    alt: "Diagnostic scan tool in use",
    ref: "IMG-REF-07041",
  },
  {
    src: "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&w=900&q=70",
    alt: "Vehicle on the lift, full view",
    ref: "IMG-REF-07058",
  },
];

export function Gallery() {
  const images = GALLERY_IMAGES.length ? GALLERY_IMAGES : FALLBACK;
  if (!images.length) return null;

  return (
    <section id="gallery" className="relative py-20 sm:py-28 border-t border-white/5">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mb-12 max-w-2xl">
          <RefCode accent>// SHOP-PHOTOS-001</RefCode>
          <h2 className="mt-3 stencil text-5xl sm:text-6xl">ON THE LIFT</h2>
        </div>

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {images.slice(0, 6).map((img, i) => (
            <motion.div
              key={img.src}
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: i * 0.05, ease: "easeOut" }}
              className="group relative aspect-square overflow-hidden border border-white/10"
            >
              <Image
                src={img.src}
                alt={img.alt}
                fill
                sizes="(min-width: 640px) 33vw, 50vw"
                className="object-cover transition-all duration-700 group-hover:scale-105"
                style={{ filter: "grayscale(0.7) contrast(1.05)" }}
              />
              <ImgRefTag code={img.ref} />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
