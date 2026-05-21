import "server-only";
import { Resend } from "resend";

/**
 * Returns a Resend client if RESEND_API_KEY is configured, otherwise null.
 * Callers should treat `null` as "email not configured" and degrade gracefully
 * (typically: still return a success response so the user gets confirmation,
 * and log a warning server-side).
 */
export function getResendClient(): Resend | null {
  const key = process.env.RESEND_API_KEY;
  if (!key) return null;
  return new Resend(key);
}

export const CONTACT_TO_EMAIL =
  process.env.CONTACT_TO_EMAIL || process.env.RESEND_TO_EMAIL || "";
export const CONTACT_FROM_EMAIL =
  process.env.CONTACT_FROM_EMAIL || "onboarding@resend.dev";
