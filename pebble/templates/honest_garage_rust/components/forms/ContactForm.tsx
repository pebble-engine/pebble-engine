"use client";
import { useFormState, useFormStatus } from "react-dom";
import { submitContactForm, type ContactFormState } from "@/app/actions/contact";
import { cn } from "@/lib/cn";

const initial: ContactFormState = { ok: false };

/**
 * Estimate-request form per the DNA's section_flow.contact spec — mono inputs,
 * NAME / PHONE / VEHICLE / ISSUE fields, full-width rust SEND REQUEST CTA.
 */
export function ContactForm() {
  const [state, action] = useFormState(submitContactForm, initial);

  return (
    <form action={action} className="space-y-4" noValidate>
      <Field label="NAME" name="name" type="text" required autoComplete="name" />
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="EMAIL" name="email" type="email" required autoComplete="email" />
        <Field label="PHONE" name="phone" type="tel" autoComplete="tel" />
      </div>
      <Field label="VEHICLE (YEAR / MAKE / MODEL)" name="vehicle" type="text" />
      <Field label="WHAT'S WRONG?" name="message" textarea required />

      <SubmitButton />

      {state.ok && state.message && (
        <p
          role="status"
          className="border border-primary/40 bg-primary/10 px-4 py-3 font-mono text-xs uppercase tracking-[0.08em] text-primary"
        >
          {state.message}
        </p>
      )}
      {!state.ok && state.error && (
        <p
          role="alert"
          className="border border-red-500/40 bg-red-500/10 px-4 py-3 font-mono text-xs uppercase tracking-[0.08em] text-red-400"
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
        "btn-primary w-full disabled:opacity-50 disabled:pointer-events-none",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-bg",
      )}
    >
      {pending ? "SENDING..." : "SEND REQUEST"}
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
    "w-full border border-white/10 bg-bg/60 px-4 py-3 font-mono text-sm text-fg placeholder:text-ghost focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-colors";
  return (
    <div>
      <label
        htmlFor={id}
        className="mb-1.5 block font-mono text-[10px] font-bold uppercase tracking-[0.14em] text-fg/60"
      >
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
