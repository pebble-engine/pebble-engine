"use client";

import { useRef, useState } from "react";
import { submitContact } from "@/app/actions/contact";
import { REASON_OPTIONS, TIME_OPTIONS } from "@/content/site";

type State = { ok: boolean; error?: string } | null;

export function BookingForm() {
  const [pending, setPending] = useState(false);
  const [result, setResult] = useState<State>(null);
  const formRef = useRef<HTMLFormElement>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setPending(true);
    setResult(null);
    const data = new FormData(e.currentTarget);
    const name   = data.get("name")?.toString()  ?? "";
    const email  = data.get("email")?.toString() ?? "";
    const phone  = data.get("phone")?.toString() ?? "";
    const date   = data.get("date")?.toString()  ?? "";
    const time   = data.get("time")?.toString()  ?? "";
    const reason = data.get("reason")?.toString() ?? "";
    const notes  = data.get("notes")?.toString() ?? "";

    const message =
      `Appointment request:\n` +
      `Phone: ${phone}\n` +
      `Preferred date: ${date}\n` +
      `Preferred time: ${time || "Anytime"}\n` +
      `Reason: ${reason}\n` +
      `Notes / Insurance: ${notes || "(none)"}`;

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
    <form
      ref={formRef}
      onSubmit={handleSubmit}
      className="space-y-6 bg-slate-50 p-8 rounded-2xl border border-slate-100 shadow-sm"
      noValidate
    >
      <h2 className="font-[family-name:var(--font-display)] text-2xl font-bold text-navy mb-2">
        Schedule Appointment
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
          <input type="text" name="name" required className="form-input-bd" placeholder="First and last name" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Phone</label>
          <input type="tel" name="phone" required className="form-input-bd" placeholder="[(555) 555-5555]" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
          <input type="email" name="email" required className="form-input-bd" placeholder="you@email.com" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Preferred Date</label>
          <input type="date" name="date" required className="form-input-bd" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Preferred Time</label>
          <select name="time" className="form-input-bd" defaultValue="">
            {TIME_OPTIONS.map((opt) => (
              <option key={opt.label} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-slate-700 mb-1">Reason for Visit</label>
          <select name="reason" className="form-input-bd" defaultValue={REASON_OPTIONS[0]}>
            {REASON_OPTIONS.map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-slate-700 mb-1">Notes / Insurance</label>
          <textarea
            name="notes"
            rows={3}
            className="form-input-bd resize-none"
            placeholder="Carrier, member ID, or any special requests..."
          />
        </div>
      </div>
      <button
        type="submit"
        disabled={pending}
        className="w-full btn-coral text-lg disabled:opacity-60"
      >
        {pending ? "Checking availability..." : "Confirm Appointment"}
      </button>
      {result && (
        <p className={`text-center text-sm font-medium ${result.ok ? "text-navy" : "text-coral"}`}>
          {result.ok
            ? "Request received! We will text/email you within 2 hours to confirm your slot."
            : (result.error ?? "Submission failed.")}
        </p>
      )}
    </form>
  );
}
