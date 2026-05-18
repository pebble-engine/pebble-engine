"use client";
import { useActionState } from "react";
import { submitContactForm } from "@/app/actions/contact";

export function ContactForm() {
  const [_, action] = useActionState(submitContactForm, null);
  return (
    <form action={action}>
      <input aria-label="Your name" name="name" required />
      <input aria-label="Email address" type="email" name="email" required />
      <textarea aria-label="Message" name="message" required />
      <button type="submit">Send</button>
    </form>
  );
}
