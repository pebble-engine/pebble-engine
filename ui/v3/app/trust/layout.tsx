import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Trust Charter — Pebble",
  description: "Pebble's GDPR, data-rights, and security commitments — with the specific evidence backing each claim.",
};

export default function TrustLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
