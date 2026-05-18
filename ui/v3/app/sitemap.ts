import type { MetadataRoute } from "next";

const BASE = process.env.NEXT_PUBLIC_BASE_URL ?? "https://pebbleapp.ai";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: `${BASE}/landing`,
      changeFrequency: "weekly",
      priority: 1.0,
    },
    {
      url: `${BASE}/pricing`,
      changeFrequency: "monthly",
      priority: 0.9,
    },
    {
      url: `${BASE}/migrate`,
      changeFrequency: "monthly",
      priority: 0.7,
    },
    {
      url: `${BASE}/login`,
      changeFrequency: "yearly",
      priority: 0.5,
    },
    {
      url: `${BASE}/signup`,
      changeFrequency: "yearly",
      priority: 0.5,
    },
    {
      url: `${BASE}/privacy`,
      changeFrequency: "yearly",
      priority: 0.3,
    },
    {
      url: `${BASE}/terms`,
      changeFrequency: "yearly",
      priority: 0.3,
    },
  ];
}
