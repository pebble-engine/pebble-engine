"use server";
import { getResendClient, CONTACT_TO_EMAIL, CONTACT_FROM_EMAIL } from "@/lib/email";
import { SITE_TITLE } from "@/content/site";

export type ContactFormState = {
  ok: boolean;
  message?: string;
  error?: string;
};

export async function submitContactForm(
  _prevState: ContactFormState | null,
  formData: FormData,
): Promise<ContactFormState> {
  const name = String(formData.get("name") ?? "").trim();
  const email = String(formData.get("email") ?? "").trim();
  const phone = String(formData.get("phone") ?? "").trim();
  const message = String(formData.get("message") ?? "").trim();

  if (!name || !email || !message) {
    return { ok: false, error: "Please provide a name, email, and message." };
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return { ok: false, error: "That email address doesn't look right." };
  }

  const resend = getResendClient();
  if (!resend || !CONTACT_TO_EMAIL) {
    console.warn(
      "[contact] RESEND_API_KEY or CONTACT_TO_EMAIL not set — message not delivered",
    );
    return { ok: true, message: "Thanks — we'll be in touch." };
  }

  try {
    await resend.emails.send({
      from: CONTACT_FROM_EMAIL,
      to: [CONTACT_TO_EMAIL],
      subject: `[${SITE_TITLE}] New contact from ${name}`,
      replyTo: email,
      text: `From: ${name} <${email}>${phone ? ` (${phone})` : ""}\n\n${message}`,
    });
    return { ok: true, message: "Thanks — we'll be in touch." };
  } catch (err) {
    const reason = err instanceof Error ? err.message : "Unknown error";
    return {
      ok: false,
      error: `Could not send right now (${reason}). Please call or email directly.`,
    };
  }
}
