"use client";
import { useActionState } from "react";
import { useFormStatus } from "react-dom";
import { submitContactForm, type ContactFormState } from "@/app/actions/contact";

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button
      type="submit"
      disabled={pending}
      className="bg-[var(--color-accent)] text-white px-8 py-3 rounded-lg font-medium hover:opacity-90 transition-opacity disabled:opacity-60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)] focus-visible:ring-offset-2 focus-visible:ring-offset-transparent min-h-[44px]" data-pebble-id="pb-a35789">
      {pending ? "Sending…" : "Send Message"}
    </button>
  );
}

export function ContactForm() {
  const [state, action] = useActionState<ContactFormState | null, FormData>(submitContactForm, null);
  return (
    <form action={action} className="space-y-4 max-w-xl">
      <input aria-label="Your name" name="name" placeholder="Your name" required className="w-full bg-[var(--color-surface-1)] border border-[var(--color-border)] rounded-lg px-4 py-3 text-white placeholder-white/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)] focus-visible:ring-offset-2 focus-visible:ring-offset-transparent" style={{ fontSize: "16px" }} />
      <input aria-label="Email address" type="email" name="email" placeholder="Email" required className="w-full bg-[var(--color-surface-1)] border border-[var(--color-border)] rounded-lg px-4 py-3 text-white placeholder-white/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)] focus-visible:ring-offset-2 focus-visible:ring-offset-transparent" style={{ fontSize: "16px" }} />
      <input aria-label="Phone number (optional)" name="phone" placeholder="Phone (optional)" className="w-full bg-[var(--color-surface-1)] border border-[var(--color-border)] rounded-lg px-4 py-3 text-white placeholder-white/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)] focus-visible:ring-offset-2 focus-visible:ring-offset-transparent" style={{ fontSize: "16px" }} />
      <textarea aria-label="Message" name="message" placeholder="How can we help?" rows={5} required className="w-full bg-[var(--color-surface-1)] border border-[var(--color-border)] rounded-lg px-4 py-3 text-white placeholder-white/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)] focus-visible:ring-offset-2 focus-visible:ring-offset-transparent" style={{ fontSize: "16px" }} />
      <SubmitButton />
      {state?.ok && (
        <p role="status" className="text-green-300" data-pebble-id="pb-ce4dcb">{state.message ?? "Sent."}</p>
      )}
      {state && state.ok === false && (
        <p role="alert" className="text-red-300" data-pebble-id="pb-4d5a88">{state.error}</p>
      )}
    </form>
  );
}