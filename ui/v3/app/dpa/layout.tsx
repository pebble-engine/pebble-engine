import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Data Processing Addendum — Pebble",
  description:
    "GDPR-aligned Data Processing Addendum for Pebble customers. Available on request.",
};

export default function DpaLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
