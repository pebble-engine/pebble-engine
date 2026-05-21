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
    message: payload.message.slice(0, 5000),
  };

  await resend.emails.send({
    from,
    to,
    replyTo: escaped.email,
    subject: `New message from ${escaped.name} via the bakery site`,
    text: `From: ${escaped.name} <${escaped.email}>\n\n${escaped.message}`,
  });
}
