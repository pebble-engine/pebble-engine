import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy — Pebble",
  description: "How Pebble collects, uses, and protects your data.",
};

export default function PrivacyLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
