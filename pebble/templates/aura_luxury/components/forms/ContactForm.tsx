"use client";

import { useRef, useState } from "react";
import { submitContact } from "@/app/actions/contact";

type State = { ok: boolean; error?: string } | null;

export function ContactForm() {
  const [pending, setPending] = useState(false);
  const [result, setResult] = useState<State>(null);
  const formRef = useRef<HTMLFormElement>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setPending(true);
    setResult(null);
    const data = new FormData(e.currentTarget);
    const res = await submitContact(data);
    setResult(res);
    setPending(false);
    if (res.ok) formRef.current?.reset();
  }

  return (
    <form ref={formRef} onSubmit={handleSubmit} className="space-y-5" noValidate>
      <div>
        <label htmlFor="name" className="block text-[10px] tracking-[0.2em] uppercase text-slate-400 font-sans mb-2">
          Name
        </label>
        <input
          id="name"
          name="name"
          type="text"
          required
          placeholder="Your Name"
          className="w-full bg-[#161920] border border-white/5 focus:border-white/30 outline-none text-sm font-sans text-white rounded-lg px-4 py-3 placeholder:text-slate-500 transition-colors"
        />
      </div>

      <div>
        <label htmlFor="email" className="block text-[10px] tracking-[0.2em] uppercase text-slate-400 font-sans mb-2">
          Email
        </label>
        <input
          id="email"
          name="email"
          type="email"
          required
          placeholder="Contact Email"
          className="w-full bg-[#161920] border border-white/5 focus:border-white/30 outline-none text-sm font-sans text-white rounded-lg px-4 py-3 placeholder:text-slate-500 transition-colors"
        />
      </div>

      <div>
        <label htmlFor="message" className="block text-[10px] tracking-[0.2em] uppercase text-slate-400 font-sans mb-2">
          Inquiry
        </label>
        <textarea
          id="message"
          name="message"
          rows={4}
          required
          placeholder="Tell us about your space..."
          className="w-full bg-[#161920] border border-white/5 focus:border-white/30 outline-none text-sm font-sans text-white rounded-lg px-4 py-3 placeholder:text-slate-500 transition-colors resize-none"
        />
      </div>

      {result && (
        <p
          className={`text-xs font-sans ${
            result.ok ? "text-emerald-400" : "text-rose-400"
          }`}
        >
          {result.ok
            ? "Inquiry received. Our concierge will respond within 15 minutes."
            : (result.error ?? "Something went wrong. Please try again.")}
        </p>
      )}

      <button
        type="submit"
        disabled={pending}
        className="w-full bg-white hover:bg-slate-200 disabled:opacity-60 transition-colors text-black text-xs font-sans font-medium uppercase tracking-[0.15em] py-3.5 rounded-lg"
      >
        {pending ? "Sending..." : "Initialize Consultation"}
      </button>
    </form>
  );
}
