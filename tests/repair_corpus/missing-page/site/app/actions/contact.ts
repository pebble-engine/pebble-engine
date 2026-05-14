"use server";

export type ContactFormState = { ok: boolean; message?: string; error?: string };

export async function submitContactForm(
  _prevState: ContactFormState | null,
  _formData: FormData,
): Promise<ContactFormState> {
  return { ok: true, message: "Thanks." };
}
