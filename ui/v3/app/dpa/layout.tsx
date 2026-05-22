import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Data Processing Addendum — Pebble",
  description: "Summary of Pebble's DPA, sub-processors, and how to request a signed copy.",
};

export default function DPALayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
