import type { Metadata } from "next";
import { Contact } from "@/components/sections/Contact";
import { SITE_TITLE } from "@/content/site";

export const metadata: Metadata = {
  title: `Book a Consult | ${SITE_TITLE}`,
};

export default function ContactPage() {
  return (
    <div className="pt-32 md:pt-40">
      <Contact />
    </div>
  );
}
