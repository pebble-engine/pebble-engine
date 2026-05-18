import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Pebble — A website built for your business, not picked from a gallery.",
  description:
    "Tell Pebble what you do. Get a unique site every time — different fonts, layout, and design DNA on every build. Free to start, no card required.",
  openGraph: {
    title: "Pebble — A website built for your business, not picked from a gallery.",
    description:
      "Tell Pebble what you do. Get a unique site every time — different fonts, layout, and design DNA on every build. Free to start.",
    images: [{ url: "/brand/desktop-pebble.png", width: 1200, height: 630 }],
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Pebble — A website built for your business",
    description:
      "Different fonts, layout, and design DNA every time. Free to start, no card required.",
    images: ["/brand/desktop-pebble.png"],
  },
};

export default function LandingLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
