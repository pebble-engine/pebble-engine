"use client";

import * as React from "react";
import { useFormState, useFormStatus } from "react-dom";
import { submitContact, type ContactState } from "@/app/actions/contact";
import { cn } from "@/lib/cn";
import { CONTACT_CTA } from "@/content/site";

const initialState: ContactState = { ok: false };

/**
 * Input — shared cinematic input style. Uppercase tracked-wide placeholders
 * with a 1px border that turns brass on focus.
 */
function Input({
  id,
  name,
  type = "text",
  placeholder,
  required = false,
  autoComplete,
}: {
  id: string;
  name: string;
  type?: string;
  placeholder: string;
  required?: boolean;
  autoComplete?: string;
}) {
  return (
    <input
      id={id}
      name={name}
      type={type}
      required={required}
      autoComplete={autoComplete}
      placeholder={placeholder}
      className={cn(
        "w-full bg-surface border border-border text-fg cinematic-radius",
        "px-5 py-4 placeholder:text-muted/70 placeholder:uppercase placeholder:tracking-[0.18em] placeholder:text-xs",
        "focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent transition-colors",
      )}
    />
  );
}

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button
      type="submit"
      disabled={pending}
      className={cn(
        "btn-cinematic w-full",
        "disabled:opacity-60 disabled:cursor-not-allowed",
      )}
    >
      {pending ? "Sending…" : CONTACT_CTA}
    </button>
  );
}

export function ContactForm() {
  const [state, formAction] = useFormState(submitContact, initialState);

  return (
    <form action={formAction} className="space-y-4" noValidate>
      {/* 2-col upper grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="name" className="sr-only">
            Name
          </label>
          <Input
            id="name"
            name="name"
            required
            autoComplete="name"
            placeholder="NAME"
          />
        </div>
        <div>
          <label htmlFor="email" className="sr-only">
            Email
          </label>
          <Input
            id="email"
            name="email"
            type="email"
            required
            autoComplete="email"
            placeholder="EMAIL"
          />
        </div>
        <div>
          <label htmlFor="phone" className="sr-only">
            Phone
          </label>
          <Input
            id="phone"
            name="phone"
            type="tel"
            autoComplete="tel"
            placeholder="PHONE"
          />
        </div>
        <div>
          <label htmlFor="target" className="sr-only">
            Target market
          </label>
          <Input
            id="target"
            name="target"
            placeholder="TARGET MARKET"
          />
        </div>
      </div>

      {/* Full-width textarea */}
      <div>
        <label htmlFor="message" className="sr-only">
          Message
        </label>
        <textarea
          id="message"
          name="message"
          rows={5}
          required
          placeholder="TELL US WHAT YOU'RE LOOKING FOR"
          className={cn(
            "w-full bg-surface border border-border text-fg cinematic-radius",
            "px-5 py-4 placeholder:text-muted/70 placeholder:uppercase placeholder:tracking-[0.18em] placeholder:text-xs",
            "focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent transition-colors resize-y",
          )}
        />
      </div>

      {/* Full-width submit */}
      <SubmitButton />

      {state.message && (
        <p
          role={state.ok ? "status" : "alert"}
          className={cn(
            "text-sm text-center pt-2",
            state.ok ? "text-fg" : "text-accent",
          )}
        >
          {state.message}
        </p>
      )}
    </form>
  );
}
