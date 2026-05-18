import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Pricing — Pebble",
  description:
    "Free to start. Starter at $29/month for unlimited sites. Pro at $59/month for multi-page sites and priority support. Visual edits always free.",
  openGraph: {
    title: "Pricing — Pebble",
    description:
      "Free to start. Starter at $29/month for unlimited sites. Pro at $59/month for multi-page sites and priority support.",
    images: [{ url: "/brand/plinth-cinematic.png", width: 1200, height: 630 }],
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Pricing — Pebble",
    description:
      "Free to start. Starter $29/mo · Pro $59/mo. Visual edits always free on every plan.",
    images: ["/brand/plinth-cinematic.png"],
  },
};

export default function PricingLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
