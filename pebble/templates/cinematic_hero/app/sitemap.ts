import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date();
  return [
    { url: "/",             lastModified: now },
    { url: "/about",        lastModified: now },
    { url: "/services",     lastModified: now },
    { url: "/gallery",      lastModified: now },
    { url: "/process",      lastModified: now },
    { url: "/faq",          lastModified: now },
    { url: "/service-area", lastModified: now },
    { url: "/contact",      lastModified: now },
  ];
}
