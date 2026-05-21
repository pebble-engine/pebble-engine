"use client";
import { useFormState, useFormStatus } from "react-dom";
import { submitContactForm, type ContactFormState } from "@/app/actions/contact";
import { cn } from "@/lib/cn";

const initial: ContactFormState = { ok: false };

export function ContactForm() {
  const [state, action] = useFormState(submitContactForm, initial);

  return (
    <form action={action} className="space-y-4" noValidate>
      <Field label="Name" name="name" type="text" required autoComplete="name" />
      <Field label="Email" name="email" type="email" required autoComplete="email" />
      <Field label="Phone (optional)" name="phone" type="tel" autoComplete="tel" />
      <Field label="How can we help?" name="message" textarea required />

      <SubmitButton />

      {state.ok && state.message && (
        <p
          role="status"
          className="rounded-xl border border-primary/40 bg-primary/10 px-4 py-3 text-sm text-primary"
        >
          {state.message}
        </p>
      )}
      {!state.ok && state.error && (
        <p
          role="alert"
          className="rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-400"
        >
          {state.error}
        </p>
      )}
    </form>
  );
}

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button
      type="submit"
      disabled={pending}
      className={cn(
        "shimmer-sweep inline-flex w-full items-center justify-center rounded-full bg-primary px-6 py-3.5 text-sm font-medium text-white transition-colors hover:bg-secondary disabled:opacity-50",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-bg",
      )}
    >
      {pending ? "Sending..." : "Send Message"}
    </button>
  );
}

type FieldProps =
  | {
      label: string;
      name: string;
      type: "text" | "email" | "tel";
      textarea?: false;
      required?: boolean;
      autoComplete?: string;
    }
  | {
      label: string;
      name: string;
      textarea: true;
      type?: undefined;
      required?: boolean;
      autoComplete?: string;
    };

function Field(props: FieldProps) {
  const id = `field-${props.name}`;
  const baseInput =
    "w-full rounded-2xl border border-border bg-card/60 px-4 py-3 text-sm text-fg placeholder:text-ghost focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40 transition-colors";
  return (
    <div>
      <label htmlFor={id} className="mb-1.5 block text-xs font-medium uppercase tracking-widest text-subtle">
        {props.label}
        {props.required ? " *" : ""}
      </label>
      {props.textarea ? (
        <textarea
          id={id}
          name={props.name}
          required={props.required}
          autoComplete={props.autoComplete}
          rows={5}
          className={baseInput}
        />
      ) : (
        <input
          id={id}
          name={props.name}
          type={props.type}
          required={props.required}
          autoComplete={props.autoComplete}
          className={baseInput}
        />
      )}
    </div>
  );
}
