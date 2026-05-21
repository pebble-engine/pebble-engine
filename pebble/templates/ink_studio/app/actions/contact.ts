"use server";

import { sendContactEmail } from "@/lib/email";

export type ContactState = {
  ok: boolean;
  message?: string;
};

function isValidEmail(s: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(s);
}

export async function submitContact(
  _prev: ContactState,
  formData: FormData,
): Promise<ContactState> {
  const name = String(formData.get("name") ?? "").trim();
  const email = String(formData.get("email") ?? "").trim();
  const message = String(formData.get("message") ?? "").trim();

  if (!name || name.length < 2) {
    return { ok: false, message: "Please share your name." };
  }
  if (!email || !isValidEmail(email)) {
    return { ok: false, message: "Please share a valid email address." };
  }
  if (!message || message.length < 8) {
    return { ok: false, message: "Please write a slightly longer note." };
  }

  try {
    await sendContactEmail({ name, email, message });
  } catch (err) {
    const detail = err instanceof Error ? err.message : "Unknown error";
    return {
      ok: false,
      message: `We couldn't send your note. (${detail})`,
    };
  }

  return {
    ok: true,
    message: "Thank you — we'll reply within two business days.",
  };
}
