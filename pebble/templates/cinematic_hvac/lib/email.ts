import { Resend } from "resend";

const resend = new Resend(process.env.RESEND_API_KEY ?? "");

export async function sendContactEmail(
  to: string,
  from: string,
  subject: string,
  body: string
): Promise<void> {
  const { error } = await resend.emails.send({
    to,
    from,
    subject,
    text: body,
  });
  if (error) throw new Error(error.message);
}

export { resend };
