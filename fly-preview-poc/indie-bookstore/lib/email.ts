import "server-only";
import { Resend } from "resend";

export function getResendClient(): Resend | null {
  const key = process.env.RESEND_API_KEY;
  if (!key) return null;
  return new Resend(key);
}

export const CONTACT_TO_EMAIL = process.env.CONTACT_TO_EMAIL || process.env.RESEND_TO_EMAIL || "";
export const CONTACT_FROM_EMAIL = process.env.CONTACT_FROM_EMAIL || "onboarding@resend.dev";