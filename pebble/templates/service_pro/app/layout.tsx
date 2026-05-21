import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import { SITE_TITLE, SITE_DESCRIPTION, PHONE, ADDRESS } from "@/content/site";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-inter",
  display: "swap",
});

const outfit = Outfit({
  subsets: ["latin"],
  weight: ["600", "700", "800"],
  variable: "--font-outfit",
  display: "swap",
});

export const viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#0a0a0a",
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
    "@type": "LocalBusiness",
    name: SITE_TITLE,
    description: SITE_DESCRIPTION,
    telephone: PHONE,
    address: {
      "@type": "PostalAddress",
      streetAddress: ADDRESS,
      addressRegion: "NY",
      addressCountry: "US",
    },
  };

  // The inline script below restores the user's theme choice before paint,
  // preventing the flash of dark-on-light (or vice versa) on first load.
  const themeBootstrap = `
    (function(){try{
      var t = localStorage.getItem('theme');
      if(!t){t = window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';}
      document.documentElement.setAttribute('data-theme', t);
    }catch(e){}})();
  `;

  return (
    <html lang="en" data-theme="dark" className={`${inter.variable} ${outfit.variable}`}>
      <body className={`${inter.className} antialiased`}>
        <script dangerouslySetInnerHTML={{ __html: themeBootstrap }} />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(ld) }}
        />
        <div className="grain-overlay" aria-hidden="true" />
        {children}
      </body>
    </html>
  );
}
