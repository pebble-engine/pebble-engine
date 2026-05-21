import type { Metadata } from "next";
import { Raleway, Lora } from "next/font/google";
import { SITE_TITLE, SITE_DESCRIPTION, PHONE, ADDRESS } from "@/content/site";
import "./globals.css";

const raleway = Raleway({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-inter",
  display: "swap",
});

const lora = Lora({
  subsets: ["latin"],
  weight: ["400", "600", "700"],
  variable: "--font-outfit",
  display: "swap",
});

export const viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#FAF8F1",
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
      if(!t){t = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';}
      document.documentElement.setAttribute('data-theme', t);
    }catch(e){}})();
  `;

  return (
    <html lang="en" data-theme="light" className={`${raleway.variable} ${lora.variable}`}>
      <body className={`${raleway.className} antialiased`}>
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
