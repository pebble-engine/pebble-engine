"use client";

import { useCallback, useEffect, useRef, useState } from "react";

const MAX = 4000;

type Props = {
  /** Friendly heading, e.g. "Tell Pebble about your business" */
  title: string;
  /** One-line helper under the heading */
  subtitle: string;
  /** Loads the current saved text */
  load: () => Promise<string>;
  /** Persists text; resolves on success */
  save: (text: string) => Promise<void>;
};

/**
 * P1 — "Tell Pebble about your business."
 *
 * A plain-language durable-context editor (NOT "custom instructions"). Used in
 * two places: per-project (workspace) and account-wide (settings). Loads the
 * saved value, autosaves ~900ms after the user stops typing, shows a clear
 * Saving/Saved state, and caps at MAX chars. Every build + edit then honors it.
 */
export function BusinessKnowledgeCard({ title, subtitle, load, save }: Props) {
  const [text, setText] = useState("");
  const [status, setStatus] = useState<"loading" | "idle" | "saving" | "saved" | "error">("loading");
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastSaved = useRef("");

  // Load ONCE on mount. We deliberately do NOT depend on `load`: callers often
  // pass an inline arrow (new identity every render), and re-running this effect
  // would re-fetch and clobber whatever the user is currently typing — wiping
  // input and spamming GETs. The ref keeps us calling the latest `load` without
  // retriggering. (Regression fix: the account-settings card lost typed text.)
  const loadRef = useRef(load);
  loadRef.current = load;
  useEffect(() => {
    let alive = true;
    loadRef.current()
      .then((v) => { if (alive) { setText(v || ""); lastSaved.current = v || ""; setStatus("idle"); } })
      .catch(() => { if (alive) setStatus("error"); });
    return () => { alive = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const doSave = useCallback(async (value: string) => {
    if (value === lastSaved.current) return;
    setStatus("saving");
    try {
      await save(value);
      lastSaved.current = value;
      setStatus("saved");
    } catch {
      setStatus("error");
    }
  }, [save]);

  const onChange = (v: string) => {
    setText(v.slice(0, MAX));
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => doSave(v.slice(0, MAX)), 900);
  };

  const onBlur = () => {
    if (timer.current) clearTimeout(timer.current);
    doSave(text);
  };

  const statusLabel =
    status === "loading" ? "Loading…"
    : status === "saving" ? "Saving…"
    : status === "saved" ? "Saved ✓"
    : status === "error" ? "Couldn't save — try again"
    : "";

  return (
    <section className="rounded-2xl border border-border bg-card p-5 sm:p-6">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-foreground">{title}</h3>
          <p className="mt-1 text-sm text-muted-foreground">{subtitle}</p>
        </div>
        <span
          className={`shrink-0 text-xs ${status === "error" ? "text-destructive" : "text-muted-foreground"}`}
          aria-live="polite"
        >
          {statusLabel}
        </span>
      </div>

      <textarea
        value={text}
        onChange={(e) => onChange(e.target.value)}
        onBlur={onBlur}
        disabled={status === "loading"}
        rows={6}
        aria-label={title}
        placeholder={
          "e.g. Hours: Mon–Sat 7am–6pm, closed Sundays.\n" +
          "Service area: Denver metro, 25-mile radius.\n" +
          "Voice: friendly and no-nonsense.\n" +
          "Always mention we're licensed & insured.\n" +
          "Never mention pricing on the site."
        }
        className="mt-4 w-full resize-y rounded-xl border border-border bg-background px-3 py-2.5 text-sm text-foreground placeholder:text-muted-foreground/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      />

      <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
        <span>Pebble uses this every time it builds or edits your site — so you only say it once.</span>
        <span>{text.length}/{MAX}</span>
      </div>
    </section>
  );
}
