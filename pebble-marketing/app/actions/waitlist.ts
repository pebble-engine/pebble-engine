"use server";
import {
  getResendClient,
  WAITLIST_TO_EMAIL,
  WAITLIST_FROM_EMAIL,
  WAITLIST_AUDIENCE_ID,
} from "@/lib/email";

export type WaitlistFormState = {
  ok: boolean;
  message?: string;
  error?: string;
};

/**
 * Server Action invoked by the waitlist form.
 * - Validates email shape.
 * - Adds the email to a Resend Audience (so Marc can email them later).
 * - Sends Marc a notification email when someone signs up.
 * - No-key path: returns ok:true with a console.warn, so local dev runs.
 */
export async function joinWaitlist(
  _prevState: WaitlistFormState | null,
  formData: FormData,
): Promise<WaitlistFormState> {
  const email = String(formData.get("email") ?? "").trim();
  const name  = String(formData.get("name")  ?? "").trim();

  if (!email) {
    return { ok: false, error: "Please enter your email." };
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return { ok: false, error: "That email address doesn't look right." };
  }

  const resend = getResendClient();
  if (!resend) {
    console.warn("[waitlist] RESEND_API_KEY not set — signup not delivered");
    return { ok: true, message: "You're on the list. We'll be in touch soon." };
  }

  try {
    // 1. Add to Resend Audience (if configured) so the list is queryable later.
    if (WAITLIST_AUDIENCE_ID) {
      await resend.contacts.create({
        email,
        firstName: name || undefined,
        audienceId: WAITLIST_AUDIENCE_ID,
      });
    }

    // 2. Notify Marc that someone joined.
    if (WAITLIST_TO_EMAIL) {
      await resend.emails.send({
        from: WAITLIST_FROM_EMAIL,
        to: [WAITLIST_TO_EMAIL],
        subject: `New Pebble waitlist signup${name ? `: ${name}` : ""}`,
        text: `Email: ${email}${name ? `\nName: ${name}` : ""}`,
      });
    }

    return { ok: true, message: "You're on the list. We'll be in touch soon." };
  } catch (err) {
    const reason = err instanceof Error ? err.message : "Unknown error";
    return { ok: false, error: `Couldn't sign you up right now (${reason}). Try again in a minute?` };
  }
}
