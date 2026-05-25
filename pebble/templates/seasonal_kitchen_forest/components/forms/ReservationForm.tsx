"use client";

import { useRef, useState } from "react";
import { submitContact } from "@/app/actions/contact";

type State = { ok: boolean; error?: string } | null;

export function ReservationForm() {
  const [pending, setPending] = useState(false);
  const [result, setResult] = useState<State>(null);
  const formRef = useRef<HTMLFormElement>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setPending(true);
    setResult(null);
    const data = new FormData(e.currentTarget);
    const name  = data.get("name")?.toString() ?? "";
    const email = data.get("email")?.toString() ?? "";
    const date  = data.get("date")?.toString() ?? "";
    const time  = data.get("time")?.toString() ?? "";
    const party = data.get("party")?.toString() ?? "";
    const notes = data.get("notes")?.toString() ?? "";
    const message = `Reservation request:\nDate: ${date} ${time}\nParty size: ${party}\nNotes: ${notes || "(none)"}`;
    const merged = new FormData();
    merged.set("name", name);
    merged.set("email", email);
    merged.set("message", message);
    const res = await submitContact(merged);
    setResult(res);
    setPending(false);
    if (res.ok) formRef.current?.reset();
  }

  return (
    <form ref={formRef} onSubmit={handleSubmit} className="max-w-2xl mx-auto space-y-8 mt-12" noValidate>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm mb-2">Name</label>
          <input type="text" name="name" required className="form-input-sk" />
        </div>
        <div>
          <label className="block text-sm mb-2">Email</label>
          <input type="email" name="email" required className="form-input-sk" />
        </div>
        <div>
          <label className="block text-sm mb-2">Date</label>
          <input type="date" name="date" required className="form-input-sk" />
        </div>
        <div>
          <label className="block text-sm mb-2">Time</label>
          <select name="time" required className="form-input-sk">
            <option value="">Select</option>
            <option value="17:00">5:00 PM</option>
            <option value="18:00">6:00 PM</option>
            <option value="19:00">7:00 PM</option>
            <option value="20:00">8:00 PM</option>
          </select>
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm mb-2">Party Size</label>
          <input type="number" name="party" min={1} max={12} required className="form-input-sk" />
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm mb-2">Special Requests</label>
          <textarea name="notes" rows={3} className="form-input-sk resize-none" />
        </div>
      </div>
      {result && (
        <p className={`text-center text-sm ${result.ok ? "text-warmgold" : "text-burgundy"}`}>
          {result.ok
            ? "Request received. We'll confirm by email shortly."
            : (result.error ?? "Submission failed.")}
        </p>
      )}
      <button
        type="submit"
        disabled={pending}
        className="bg-burgundy text-bone w-full py-4 font-medium tracking-wide hover:bg-charcoal transition-colors disabled:opacity-60"
      >
        {pending ? "Sending..." : "Request Table"}
      </button>
    </form>
  );
}
