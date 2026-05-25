"use client";

import { useRef, useState } from "react";
import { submitContact } from "@/app/actions/contact";

type State = { ok: boolean; error?: string } | null;

export function EventForm() {
  const [pending, setPending] = useState(false);
  const [result, setResult] = useState<State>(null);
  const [guests, setGuests] = useState(20);
  const formRef = useRef<HTMLFormElement>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setPending(true);
    setResult(null);
    const data = new FormData(e.currentTarget);
    const merged = new FormData();
    merged.set("name", data.get("name")?.toString() ?? "");
    merged.set("email", data.get("email")?.toString() ?? "");
    merged.set("message", `Private event request — estimated ${guests} guests.`);
    const res = await submitContact(merged);
    setResult(res);
    setPending(false);
    if (res.ok) formRef.current?.reset();
  }

  return (
    <form ref={formRef} onSubmit={handleSubmit} className="space-y-8" noValidate>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm mb-2">Contact Name</label>
          <input type="text" name="name" required className="form-input-sk" />
        </div>
        <div>
          <label className="block text-sm mb-2">Email</label>
          <input type="email" name="email" required className="form-input-sk" />
        </div>
      </div>
      <div className="flex flex-col items-center gap-4">
        <label className="text-sm">Estimated Guest Count</label>
        <div className="flex items-center gap-4 justify-center">
          <button
            type="button"
            onClick={() => setGuests((g) => Math.max(2, g - 2))}
            className="bg-charcoal text-bone w-10 h-10 rounded-full hover:bg-burgundy transition-colors"
            aria-label="Decrease guest count"
          >
            −
          </button>
          <span className="text-2xl font-[family-name:var(--font-display)] w-16 text-center">
            {guests}
          </span>
          <button
            type="button"
            onClick={() => setGuests((g) => Math.min(200, g + 2))}
            className="bg-charcoal text-bone w-10 h-10 rounded-full hover:bg-burgundy transition-colors"
            aria-label="Increase guest count"
          >
            +
          </button>
        </div>
      </div>
      {result && (
        <p className={`text-center text-sm ${result.ok ? "text-warmgold" : "text-burgundy"}`}>
          {result.ok ? "Inquiry received. We'll reach out within the day." : (result.error ?? "Submission failed.")}
        </p>
      )}
      <button
        type="submit"
        disabled={pending}
        className="bg-burgundy text-bone w-full py-4 font-medium tracking-wide hover:bg-charcoal transition-colors disabled:opacity-60"
      >
        {pending ? "Sending..." : "Request Event Details"}
      </button>
    </form>
  );
}
