"use client";
import { useFormState, useFormStatus } from "react-dom";
import { submitContactForm, type ContactFormState } from "@/app/actions/contact";
import { COURSES } from "@/content/site";
import { cn } from "@/lib/cn";

const initial: ContactFormState = { ok: false };

/**
 * Enrollment form. Includes an optional course dropdown that pulls from
 * the COURSES constant so the customer's catalog stays in sync.
 */
export function ContactForm() {
  const [state, action] = useFormState(submitContactForm, initial);

  return (
    <form action={action} className="space-y-4" noValidate>
      <Field label="Name" name="name" type="text" required autoComplete="name" />
      <Field label="Email" name="email" type="email" required autoComplete="email" />
      <Field label="Phone (optional)" name="phone" type="tel" autoComplete="tel" />

      {COURSES.length > 0 && (
        <SelectField label="Course of interest (optional)" name="course">
          <option value="">— Choose a course —</option>
          {COURSES.map((c) => (
            <option key={c.id} value={c.name}>
              {c.name} · {c.level}
            </option>
          ))}
        </SelectField>
      )}

      <Field label="Your message" name="message" textarea required />

      <SubmitButton />

      {state.ok && state.message && (
        <p
          role="status"
          className="rounded-xl border border-accent/40 bg-accent/10 px-4 py-3 text-sm text-accent"
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
        "shimmer-band inline-flex w-full items-center justify-center rounded-full bg-accent px-6 py-3.5 text-sm font-bold uppercase tracking-wide-12 text-fg transition-colors hover:bg-[hsl(var(--accent-light))] disabled:opacity-50",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-bg",
      )}
    >
      {pending ? "Sending..." : "Send Inquiry"}
    </button>
  );
}

type TextFieldProps = {
  label: string;
  name: string;
  type: "text" | "email" | "tel";
  textarea?: false;
  required?: boolean;
  autoComplete?: string;
};
type TextareaFieldProps = {
  label: string;
  name: string;
  textarea: true;
  type?: undefined;
  required?: boolean;
  autoComplete?: string;
};
type FieldProps = TextFieldProps | TextareaFieldProps;

const baseInput =
  "w-full rounded-2xl border border-border bg-card/60 px-4 py-3 text-sm text-fg placeholder:text-ghost focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/40 transition-colors";

function Field(props: FieldProps) {
  const id = `field-${props.name}`;
  return (
    <div>
      <label
        htmlFor={id}
        className="mb-1.5 block text-[10px] font-bold uppercase tracking-wide-15 text-subtle"
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

function SelectField({
  label,
  name,
  children,
}: {
  label: string;
  name: string;
  children: React.ReactNode;
}) {
  const id = `field-${name}`;
  return (
    <div>
      <label
        htmlFor={id}
        className="mb-1.5 block text-[10px] font-bold uppercase tracking-wide-15 text-subtle"
      >
        {label}
      </label>
      <select id={id} name={name} className={baseInput} defaultValue="">
        {children}
      </select>
    </div>
  );
}
