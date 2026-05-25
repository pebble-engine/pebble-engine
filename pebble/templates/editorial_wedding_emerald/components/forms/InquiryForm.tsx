"use client";

import { useRef, useState } from "react";
import { submitContact } from "@/app/actions/contact";

type State = { ok: boolean; error?: string } | null;

export function InquiryForm() {
  const [pending, setPending] = useState(false);
  const [result, setResult] = useState<State>(null);
  const formRef = useRef<HTMLFormElement>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setPending(true);
    setResult(null);
    const data = new FormData(e.currentTarget);

    const partnerOne = data.get("partner_one")?.toString() ?? "";
    const partnerTwo = data.get("partner_two")?.toString() ?? "";
    const date       = data.get("wedding_date")?.toString() ?? "";
    const venue      = data.get("venue")?.toString() ?? "";
    const story      = data.get("story")?.toString() ?? "";
    const source     = data.get("source")?.toString() ?? "";

    const message = [
      `Wedding date: ${date}`,
      `Venue: ${venue}`,
      `Heard via: ${source}`,
      "",
      "Story:",
      story,
    ].join("\n");

    const merged = new FormData();
    merged.set("name", `${partnerOne} & ${partnerTwo}`.trim());
    merged.set("email", data.get("email")?.toString() ?? "");
    merged.set("message", message);

    const res = await submitContact(merged);
    setResult(res);
    setPending(false);
    if (res.ok) formRef.current?.reset();
  }

  return (
    <form ref={formRef} onSubmit={handleSubmit} className="space-y-8" noValidate>
      <div className="grid md:grid-cols-2 gap-8">
        <div>
          <label className="block text-xs uppercase tracking-widest text-[#f5f0dc]/40 mb-2">Partner One</label>
          <input type="text" name="partner_one" required placeholder="Full name" className="form-input-ed" />
        </div>
        <div>
          <label className="block text-xs uppercase tracking-widest text-[#f5f0dc]/40 mb-2">Partner Two</label>
          <input type="text" name="partner_two" required placeholder="Full name" className="form-input-ed" />
        </div>
      </div>
      <div className="grid md:grid-cols-2 gap-8">
        <div>
          <label className="block text-xs uppercase tracking-widest text-[#f5f0dc]/40 mb-2">Email</label>
          <input type="email" name="email" required placeholder="you@example.com" className="form-input-ed" />
        </div>
        <div>
          <label className="block text-xs uppercase tracking-widest text-[#f5f0dc]/40 mb-2">Wedding Date</label>
          <input type="text" name="wedding_date" required placeholder="[MM/DD/YYYY]" className="form-input-ed" />
        </div>
      </div>
      <div>
        <label className="block text-xs uppercase tracking-widest text-[#f5f0dc]/40 mb-2">Venue / Location</label>
        <input type="text" name="venue" required placeholder="[Venue Name, City]" className="form-input-ed" />
      </div>
      <div>
        <label className="block text-xs uppercase tracking-widest text-[#f5f0dc]/40 mb-2">Tell us your story</label>
        <textarea name="story" rows={4} placeholder="How you met, what you're planning, what matters most..." className="form-input-ed resize-none" />
      </div>
      <div>
        <label className="block text-xs uppercase tracking-widest text-[#f5f0dc]/40 mb-2">How did you find us?</label>
        <select name="source" className="form-input-ed bg-[#0a2820]">
          <option value="">Select one</option>
          <option>Instagram</option>
          <option>Referral / Friend</option>
          <option>Wedding Blog / Magazine</option>
          <option>Search / Google</option>
          <option>Other</option>
        </select>
      </div>
      {result && (
        <p className={`text-center text-sm ${result.ok ? "text-[#dcb780]" : "text-rose-400"}`}>
          {result.ok
            ? "Thank you — I'll be in touch within 48 hours."
            : (result.error ?? "Submission failed. Please try again.")}
        </p>
      )}
      <button type="submit" disabled={pending} className="btn-brass w-full text-center disabled:opacity-60">
        {pending ? "Sending..." : "Send Inquiry"}
      </button>
    </form>
  );
}
