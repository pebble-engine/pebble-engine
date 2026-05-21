import type { Metadata } from "next";
import { Share_Tech_Mono, Fira_Code } from "next/font/google";
import { SITE_TITLE, SITE_DESCRIPTION, PHONE, ADDRESS } from "@/content/site";
import "./globals.css";

// Share Tech Mono is the sci-fi HUD display face.
const sharetech = Share_Tech_Mono({
  subsets: ["latin"],
  weight: ["400"],
  variable: "--font-anton",
  display: "swap",
});

// Fira Code is the developer mono for UI + code.
const firacode = Fira_Code({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

export const viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#1A1D14",
};

export const metadata: Metadata = {
  title: `${SITE_TITLE} — ${SITE_DESCRIPTION}`,
  description: SITE_DESCRIPTION,
  openGraph: {
    title: SITE_TITLE,
    description: SITE_DESCRIPTION,
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: SITE_TITLE,
    description: SITE_DESCRIPTION,
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const ld = {
    "@context": "https://schema.org",
    "@type": "AutoRepair",
    name: SITE_TITLE,
    description: SITE_DESCRIPTION,
    telephone: PHONE,
    address: {
      "@type": "PostalAddress",
      streetAddress: ADDRESS,
      addressCountry: "US",
    },
  };

  return (
    <html
      lang="en"
      className={`${sharetech.variable} ${firacode.variable}`}
    >
      <body className={`${firacode.className} antialiased`}>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(ld) }}
        />
        {/* The load-bearing hazard stripe. Sits above the nav on every page. */}
        <div className="hazard-stripe" aria-hidden="true" />
        {children}
      </body>
    </html>
  );
}
