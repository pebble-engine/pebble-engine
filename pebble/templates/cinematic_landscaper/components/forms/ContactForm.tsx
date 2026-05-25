"use client";

import { useRef, useState } from "react";
import { submitContact } from "@/app/actions/contact";
import { Button } from "@/components/ui/Button";

type State = { ok: boolean; error?: string } | null;

export function ContactForm() {
  const [pending, setPending] = useState(false);
  const [result, setResult] = useState<State>(null);
  const formRef = useRef<HTMLFormElement>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setPending(true);
    setResult(null);
    const data = new FormData(e.currentTarget);
    const res = await submitContact(data);
    setResult(res);
    setPending(false);
    if (res.ok) formRef.current?.reset();
  }

  return (
    <form ref={formRef} onSubmit={handleSubmit} className="space-y-5" noValidate>
      <div>
        <label
          htmlFor="name"
          className="block text-[13px] font-semibold text-[var(--color-text-primary)] mb-1.5"
        >
          Name
        </label>
        <input
          id="name"
          name="name"
          type="text"
          required
          placeholder="Jane Smith"
          className="w-full h-12 px-4 rounded-lg border border-[var(--color-border)] bg-white text-[var(--color-text-primary)] placeholder:text-[var(--color-text-secondary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent transition"
        />
      </div>

      <div>
        <label
          htmlFor="email"
          className="block text-[13px] font-semibold text-[var(--color-text-primary)] mb-1.5"
        >
          Email
        </label>
        <input
          id="email"
          name="email"
          type="email"
          required
          placeholder="jane@example.com"
          className="w-full h-12 px-4 rounded-lg border border-[var(--color-border)] bg-white text-[var(--color-text-primary)] placeholder:text-[var(--color-text-secondary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent transition"
        />
      </div>

      <div>
        <label
          htmlFor="message"
          className="block text-[13px] font-semibold text-[var(--color-text-primary)] mb-1.5"
        >
          Message
        </label>
        <textarea
          id="message"
          name="message"
          rows={5}
          required
          placeholder="Tell us what you need…"
          className="w-full px-4 py-3 rounded-lg border border-[var(--color-border)] bg-white text-[var(--color-text-primary)] placeholder:text-[var(--color-text-secondary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent transition resize-none"
        />
      </div>

      {result && (
        <p
          className={`text-[14px] font-medium ${
            result.ok
              ? "text-green-700"
              : "text-red-600"
          }`}
        >
          {result.ok
            ? "Message sent! We'll be in touch soon."
            : (result.error ?? "Something went wrong. Please try again.")}
        </p>
      )}

      <Button type="submit" disabled={pending} size="lg" className="w-full md:w-auto">
        {pending ? "Sending…" : "Send message"}
      </Button>
    </form>
  );
}
