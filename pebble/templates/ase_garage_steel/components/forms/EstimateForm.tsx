"use client";

import { useRef, useState } from "react";
import { submitContact } from "@/app/actions/contact";

type State = { ok: boolean; error?: string } | null;

export function EstimateForm() {
  const [pending, setPending] = useState(false);
  const [result, setResult] = useState<State>(null);
  const formRef = useRef<HTMLFormElement>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setPending(true);
    setResult(null);
    const data = new FormData(e.currentTarget);
    // Pack the vehicle details into the universal "message" field
    const vehicle = data.get("vehicle")?.toString() ?? "";
    const mileage = data.get("mileage")?.toString() ?? "";
    const phone   = data.get("phone")?.toString() ?? "";
    const issue   = data.get("issue")?.toString() ?? "";
    const message = `Vehicle: ${vehicle}\nMileage: ${mileage}\nPhone: ${phone}\n\nIssue:\n${issue}`;
    const merged = new FormData();
    merged.set("name", data.get("name")?.toString() ?? "");
    merged.set("email", data.get("email")?.toString() ?? phone);
    merged.set("message", message);
    const res = await submitContact(merged);
    setResult(res);
    setPending(false);
    if (res.ok) formRef.current?.reset();
  }

  return (
    <form ref={formRef} onSubmit={handleSubmit} className="space-y-6" noValidate>
      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <label className="block text-xs uppercase tracking-wider text-[#e7e5e4]/70 mb-1">Year / Make / Model</label>
          <input
            type="text"
            name="vehicle"
            placeholder="e.g. 2018 Ford Explorer"
            required
            className="w-full bg-[#1e3a5f]/80 border border-[#e7e5e4]/20 p-3 text-[#fafaf9] focus:border-[#3b82f6] focus:outline-none transition-colors"
          />
        </div>
        <div>
          <label className="block text-xs uppercase tracking-wider text-[#e7e5e4]/70 mb-1">Mileage</label>
          <input
            type="number"
            name="mileage"
            placeholder="e.g. 64000"
            required
            className="w-full bg-[#1e3a5f]/80 border border-[#e7e5e4]/20 p-3 text-[#fafaf9] focus:border-[#3b82f6] focus:outline-none transition-colors"
          />
        </div>
      </div>
      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <label className="block text-xs uppercase tracking-wider text-[#e7e5e4]/70 mb-1">Contact Name</label>
          <input
            type="text"
            name="name"
            required
            className="w-full bg-[#1e3a5f]/80 border border-[#e7e5e4]/20 p-3 text-[#fafaf9] focus:border-[#3b82f6] focus:outline-none transition-colors"
          />
        </div>
        <div>
          <label className="block text-xs uppercase tracking-wider text-[#e7e5e4]/70 mb-1">Email or Phone</label>
          <input
            type="text"
            name="email"
            placeholder="you@example.com or (555) 123-4567"
            required
            className="w-full bg-[#1e3a5f]/80 border border-[#e7e5e4]/20 p-3 text-[#fafaf9] focus:border-[#3b82f6] focus:outline-none transition-colors"
          />
        </div>
      </div>
      <div>
        <label className="block text-xs uppercase tracking-wider text-[#e7e5e4]/70 mb-2">What&apos;s Wrong? (Be blunt)</label>
        <textarea
          name="issue"
          rows={4}
          placeholder="e.g. Grinding when braking, check engine code P0420, AC blowing warm..."
          required
          className="w-full bg-[#1e3a5f]/80 border border-[#e7e5e4]/20 p-3 text-[#fafaf9] focus:border-[#3b82f6] focus:outline-none transition-colors resize-none"
        />
      </div>
      <input type="hidden" name="phone" value="" />
      <div className="text-xs text-[#e7e5e4]/40 mb-4 text-center border-t border-[#e7e5e4]/10 pt-4">
        Photos optional. Drag &amp; drop [VIN / OBD-II scan / damage] here or bring to shop.
      </div>
      {result && (
        <p className={`text-center text-sm ${result.ok ? "text-[#3b82f6]" : "text-[#fb7185]"}`}>
          {result.ok ? "Request received. We'll text or call your slot shortly." : (result.error ?? "Submission failed. Please try again.")}
        </p>
      )}
      <button
        type="submit"
        disabled={pending}
        className="w-full btn-shimmer py-4 text-lg font-bold uppercase tracking-wide rounded-sm disabled:opacity-60"
      >
        {pending ? "Sending..." : "Submit For Diagnostic Slot"}
      </button>
    </form>
  );
}
