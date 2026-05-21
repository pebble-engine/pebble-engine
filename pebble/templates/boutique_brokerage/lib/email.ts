import { Resend } from "resend";

/**
 * Single Resend instance. Reads RESEND_API_KEY from env at call time so that
 * missing env vars produce a clear runtime error instead of failing at import.
 */
let _client: Resend | null = null;

export function getResend(): Resend {
  if (_client) return _client;
  const key = process.env.RESEND_API_KEY;
  if (!key) {
    throw new Error(
      "RESEND_API_KEY is not set. Add it to .env (see .env.example).",
    );
  }
  _client = new Resend(key);
  return _client;
}

export type ContactPayload = {
  name: string;
  email: string;
  phone?: string;
  target?: string;
  message: string;
};

export async function sendContactEmail(payload: ContactPayload): Promise<void> {
  const from = process.env.CONTACT_FROM_EMAIL;
  const to = process.env.CONTACT_TO_EMAIL;
  if (!from || !to) {
    throw new Error(
      "CONTACT_FROM_EMAIL and CONTACT_TO_EMAIL must be set in .env.",
    );
  }

  const resend = getResend();
  const escaped = {
    name: payload.name.slice(0, 200),
    email: payload.email.slice(0, 200),
    phone: (payload.phone ?? "").slice(0, 50),
    target: (payload.target ?? "").slice(0, 200),
    message: payload.message.slice(0, 5000),
  };

  const lines = [
    `From: ${escaped.name} <${escaped.email}>`,
    escaped.phone ? `Phone: ${escaped.phone}` : null,
    escaped.target ? `Target market: ${escaped.target}` : null,
    "",
    escaped.message,
  ].filter(Boolean);

  await resend.emails.send({
    from,
    to,
    replyTo: escaped.email,
    subject: `Confidential inquiry from ${escaped.name}`,
    text: lines.join("\n"),
  });
}
