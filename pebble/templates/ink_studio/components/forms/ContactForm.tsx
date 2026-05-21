"use client";

import * as React from "react";
import { useFormState, useFormStatus } from "react-dom";
import { submitContact, type ContactState } from "@/app/actions/contact";
import { cn } from "@/lib/cn";

const initialState: ContactState = { ok: false };

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button
      type="submit"
      disabled={pending}
      className={cn(
        "inline-flex items-center justify-center px-8 py-4 text-button transition-all duration-300 ease-out",
        "bg-ink-primary text-ink-bg hover:bg-ink-gold-light hover:shadow-gold active:scale-[0.98]",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink-primary focus-visible:ring-offset-2 focus-visible:ring-offset-ink-bg",
        "disabled:opacity-60 disabled:cursor-not-allowed",
      )}
    >
      {pending ? "Sending…" : "Send Inquiry"}
    </button>
  );
}

export function ContactForm() {
  const [state, formAction] = useFormState(submitContact, initialState);

  return (
    <form action={formAction} className="space-y-5" noValidate>
      <div>
        <label htmlFor="name" className="block text-label mb-2">
          Your name
        </label>
        <input
          id="name"
          name="name"
          type="text"
          required
          autoComplete="name"
          className="w-full border border-ink-border bg-ink-card px-5 py-3.5 text-ink-fg placeholder:text-ink-muted focus:border-ink-primary focus:outline-none focus:ring-1 focus:ring-ink-primary transition-all"
          placeholder="Jane Doe"
        />
      </div>

      <div>
        <label htmlFor="email" className="block text-label mb-2">
          Email
        </label>
        <input
          id="email"
          name="email"
          type="email"
          required
          autoComplete="email"
          className="w-full border border-ink-border bg-ink-card px-5 py-3.5 text-ink-fg placeholder:text-ink-muted focus:border-ink-primary focus:outline-none focus:ring-1 focus:ring-ink-primary transition-all"
          placeholder="you@example.com"
        />
      </div>

      <div>
        <label htmlFor="message" className="block text-label mb-2">
          Tell us about your piece
        </label>
        <textarea
          id="message"
          name="message"
          rows={5}
          required
          className="w-full border border-ink-border bg-ink-card px-5 py-3.5 text-ink-fg placeholder:text-ink-muted focus:border-ink-primary focus:outline-none focus:ring-1 focus:ring-ink-primary transition-all resize-y"
          placeholder="What are you thinking? Placement, size, references…"
        />
      </div>

      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pt-2">
        <SubmitButton />
        {state.message && (
          <p
            role={state.ok ? "status" : "alert"}
            className={cn(
              "text-sm",
              state.ok ? "text-ink-primary" : "text-ink-blood-light",
            )}
          >
            {state.message}
          </p>
        )}
      </div>
    </form>
  );
}
