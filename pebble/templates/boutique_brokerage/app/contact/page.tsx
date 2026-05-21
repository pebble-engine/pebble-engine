import type { Metadata } from "next";
import { Contact } from "@/components/sections/Contact";
import { SITE_TITLE } from "@/content/site";

export const metadata: Metadata = {
  title: `Contact | ${SITE_TITLE}`,
};

export default function ContactPage() {
  return <Contact />;
}
