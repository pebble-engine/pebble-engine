import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: "/",         lastModified: new Date() },
    { url: "/about",    lastModified: new Date() },
    { url: "/services", lastModified: new Date() },
    { url: "/contact",  lastModified: new Date() },
  ];
}
