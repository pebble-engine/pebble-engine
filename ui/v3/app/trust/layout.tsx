import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Trust Commitment — Pebble",
  description: "Pebble's GDPR, data-rights, and security commitments — self-attested, with plain-language evidence backing each claim.",
};

export default function TrustLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
