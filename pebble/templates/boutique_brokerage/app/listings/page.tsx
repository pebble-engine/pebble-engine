import type { Metadata } from "next";
import { Listings } from "@/components/sections/Listings";
import { SITE_TITLE } from "@/content/site";

export const metadata: Metadata = {
  title: `Inventory | ${SITE_TITLE}`,
};

export default function ListingsPage() {
  return (
    <div className="pt-24 md:pt-32">
      <Listings />
    </div>
  );
}
