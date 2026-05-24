// Static-export compatibility note:
// When PEBBLE_PREVIEW_BUILD=1 (set during `next build` for the preview gallery),
// this file is a client-safe no-op stub — no "use server", no Resend import.
// Next.js 14.x with output:"export" rejects "use server" at build time, so
// this file must stay free of that directive when building the static skin.
//
// For customer instantiations (real projects cloned from this template):
// - They do NOT set PEBBLE_PREVIEW_BUILD.
// - They run `next dev` / `next start`, NOT static export.
// - Replace this file's body with the real server-action version (preserved
//   in git history) so Resend sends actual emails.
//
// ContactForm.tsx uses `onSubmit` (not a native form `action={...}`), so it
// calls submitContact() as a plain async function — no React server-action
// dispatch magic is needed. This stub works identically from the form's POV.

type Result = { ok: true } | { ok: false; error: string };

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export async function submitContact(formData: FormData): Promise<Result> {
  // Preview-build stub: validate client-side only, skip email send.
  // In a real customer project, replace this function with the "use server"
  // version that imports sendContactEmail from @/lib/email.
  const name    = (formData.get("name")    as string | null)?.trim() ?? "";
  const email   = (formData.get("email")   as string | null)?.trim() ?? "";
  const message = (formData.get("message") as string | null)?.trim() ?? "";

  if (!name)                 return { ok: false, error: "Name is required." };
  if (!email)                return { ok: false, error: "Email is required." };
  if (!EMAIL_RE.test(email)) return { ok: false, error: "Please enter a valid email address." };
  if (!message)              return { ok: false, error: "Message is required." };

  if (typeof window !== "undefined") {
    console.log("[preview-build contact] form submission stubbed — no email sent.");
  }
  return { ok: true };
}
