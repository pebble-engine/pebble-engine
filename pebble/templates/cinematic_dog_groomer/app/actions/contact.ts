"use server";

import { sendContactEmail } from "@/lib/email";

type Result = { ok: true } | { ok: false; error: string };

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export async function submitContact(formData: FormData): Promise<Result> {
  const name    = (formData.get("name")    as string | null)?.trim() ?? "";
  const email   = (formData.get("email")   as string | null)?.trim() ?? "";
  const message = (formData.get("message") as string | null)?.trim() ?? "";

  if (!name)               return { ok: false, error: "Name is required." };
  if (!email)              return { ok: false, error: "Email is required." };
  if (!EMAIL_RE.test(email)) return { ok: false, error: "Please enter a valid email address." };
  if (!message)            return { ok: false, error: "Message is required." };

  const to      = process.env.CONTACT_TO_EMAIL ?? "";
  const from    = process.env.CONTACT_FROM_EMAIL ?? "noreply@example.com";
  const subject = `New contact form message from ${name}`;
  const body    = `Name: ${name}\nEmail: ${email}\n\nMessage:\n${message}`;

  if (!to) {
    console.warn("[contact] CONTACT_TO_EMAIL is not set — skipping email send.");
    return { ok: true };
  }

  try {
    await sendContactEmail(to, from, subject, body);
    return { ok: true };
  } catch (err) {
    console.error("[contact] Failed to send email:", err);
    return { ok: false, error: "Failed to send your message. Please try again later." };
  }
}
