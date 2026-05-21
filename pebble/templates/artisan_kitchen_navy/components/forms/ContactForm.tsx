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
        "btn-primary",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-crust focus-visible:ring-offset-2 focus-visible:ring-offset-cream",
        "disabled:opacity-60 disabled:cursor-not-allowed",
      )}
    >
      {pending ? "Sending…" : "Send message"}
    </button>
  );
}

const fieldClasses =
  "w-full rounded-2xl border border-edge bg-cream/60 px-5 py-3.5 text-ink placeholder:text-ink-soft/60 focus:border-crust focus:outline-none focus:ring-2 focus:ring-crust/25 transition-all";

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
          className={fieldClasses}
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
          className={fieldClasses}
          placeholder="you@example.com"
        />
      </div>

      <div>
        <label htmlFor="message" className="block text-label mb-2">
          Message
        </label>
        <textarea
          id="message"
          name="message"
          rows={5}
          required
          className={cn(fieldClasses, "resize-y")}
          placeholder="What can we help with?"
        />
      </div>

      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pt-2">
        <SubmitButton />
        {state.message && (
          <p
            role={state.ok ? "status" : "alert"}
            className={cn("text-sm", state.ok ? "text-herb" : "text-crust")}
          >
            {state.message}
          </p>
        )}
      </div>
    </form>
  );
}
