import "server-only";
import { Resend } from "resend";

/**
 * Centralized Resend client.
 * Returns null when no key is set so local dev runs cleanly without credentials.
 * Mirrors the pattern used in the Pebble engine's generated contact forms.
 */
export function getResendClient(): Resend | null {
  const key = process.env.RESEND_API_KEY;
  if (!key) return null;
  return new Resend(key);
}

export const WAITLIST_TO_EMAIL   = process.env.WAITLIST_TO_EMAIL   || "";
export const WAITLIST_FROM_EMAIL = process.env.WAITLIST_FROM_EMAIL || "onboarding@resend.dev";
export const WAITLIST_AUDIENCE_ID = process.env.WAITLIST_AUDIENCE_ID || "";
