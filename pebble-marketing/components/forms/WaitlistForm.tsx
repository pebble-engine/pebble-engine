"use client";
import { useActionState } from "react";
import { useFormStatus } from "react-dom";
import { joinWaitlist, type WaitlistFormState } from "@/app/actions/waitlist";

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button
      type="submit"
      disabled={pending}
      className="
        bg-spark text-stone
        px-6 py-3 rounded-button font-medium
        hover:bg-earth hover:text-sand transition-colors
        focus-visible:outline-none focus-visible:ring-2
        focus-visible:ring-stone/60 focus-visible:ring-offset-2
        focus-visible:ring-offset-sand
        disabled:opacity-60 disabled:cursor-not-allowed
        whitespace-nowrap
      "
    >
      {pending ? "Adding you…" : "Join the waitlist"}
    </button>
  );
}

export function WaitlistForm() {
  const [state, action] = useActionState<WaitlistFormState | null, FormData>(
    joinWaitlist,
    null,
  );

  return (
    <form action={action} className="w-full max-w-md">
      <div className="flex flex-col sm:flex-row gap-3">
        <input
          name="email"
          type="email"
          required
          placeholder="you@example.com"
          aria-label="Email address"
          className="
            flex-1 bg-white border border-mist
            rounded-input px-4 py-3 text-stone placeholder-stone/40
            focus-visible:outline-none focus-visible:ring-2
            focus-visible:ring-spark/60 focus-visible:border-spark
          "
        />
        <SubmitButton />
      </div>

      {/* Optional name field hidden by default; shown after focus on a fuller version later */}

      {state?.ok && (
        <p role="status" className="mt-3 text-river text-sm">
          ✓ {state.message ?? "You're on the list."}
        </p>
      )}
      {state && state.ok === false && (
        <p role="alert" className="mt-3 text-stone/70 text-sm">
          {state.error}
        </p>
      )}

      <p className="mt-3 text-xs text-stone/50">
        We&apos;ll send one email when Pebble opens to early access. No spam.
      </p>
    </form>
  );
}
