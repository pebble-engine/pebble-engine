"use client";

/**
 * Inbox settings panel — webhook URL + autoresponder config for one project.
 *
 * The two backends shipped in commits de65433 (outbound webhook) and
 * 7e77f08 (autoresponder) had no UI. This panel is the minimal
 * functional surface so users can actually configure them. Marc
 * polishes the styling later; the goal here is end-to-end usability.
 */

import { useEffect, useState } from "react";
import {
  fetchWebhookConfig,
  setWebhookConfig,
  clearWebhookConfig,
  fetchAutoresponder,
  saveAutoresponder,
  clearAutoresponder,
  type WebhookConfig,
  type AutoresponderConfig,
} from "@/lib/api";

type SaveState = "idle" | "saving" | "saved" | "error";

export function InboxSettings({ slug }: { slug: string }) {
  // ---- Webhook state ----
  const [webhook, setWebhook] = useState<WebhookConfig | null>(null);
  const [webhookUrl, setWebhookUrl] = useState("");
  const [webhookState, setWebhookState] = useState<SaveState>("idle");
  const [webhookError, setWebhookError] = useState<string | null>(null);

  // ---- Autoresponder state ----
  const [ar, setAr] = useState<AutoresponderConfig | null>(null);
  const [arEnabled, setArEnabled] = useState(false);
  const [arSubject, setArSubject] = useState("");
  const [arBody, setArBody] = useState("");
  const [arReplyField, setArReplyField] = useState("email");
  const [arState, setArState] = useState<SaveState>("idle");
  const [arError, setArError] = useState<string | null>(null);

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      try {
        const [wh, autoresp] = await Promise.all([
          fetchWebhookConfig(slug),
          fetchAutoresponder(slug),
        ]);
        if (cancelled) return;
        setWebhook(wh.webhook);
        setWebhookUrl(wh.webhook?.url || "");
        setAr(autoresp.autoresponder);
        setArEnabled(autoresp.autoresponder.enabled);
        setArSubject(autoresp.autoresponder.subject);
        setArBody(autoresp.autoresponder.body);
        setArReplyField(autoresp.autoresponder.reply_field || "email");
      } catch (e) {
        if (!cancelled) {
          setWebhookError(e instanceof Error ? e.message : String(e));
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void load();
    return () => { cancelled = true; };
  }, [slug]);

  async function saveWebhook() {
    setWebhookState("saving");
    setWebhookError(null);
    try {
      const resp = await setWebhookConfig(slug, webhookUrl.trim());
      setWebhook(resp.webhook);
      setWebhookState("saved");
      setTimeout(() => setWebhookState("idle"), 2000);
    } catch (e) {
      setWebhookError(e instanceof Error ? e.message : String(e));
      setWebhookState("error");
    }
  }

  async function removeWebhook() {
    if (!confirm("Remove the configured webhook URL?")) return;
    setWebhookState("saving");
    setWebhookError(null);
    try {
      await clearWebhookConfig(slug);
      setWebhook(null);
      setWebhookUrl("");
      setWebhookState("saved");
      setTimeout(() => setWebhookState("idle"), 2000);
    } catch (e) {
      setWebhookError(e instanceof Error ? e.message : String(e));
      setWebhookState("error");
    }
  }

  async function saveAr() {
    setArState("saving");
    setArError(null);
    try {
      const resp = await saveAutoresponder(slug, {
        enabled:     arEnabled,
        subject:     arSubject,
        body:        arBody,
        reply_field: arReplyField,
      });
      setAr(resp.autoresponder);
      setArState("saved");
      setTimeout(() => setArState("idle"), 2000);
    } catch (e) {
      setArError(e instanceof Error ? e.message : String(e));
      setArState("error");
    }
  }

  async function resetAr() {
    if (!confirm("Reset autoresponder to defaults? This disables it and clears your custom subject + body.")) return;
    setArState("saving");
    setArError(null);
    try {
      await clearAutoresponder(slug);
      // Reload defaults from the server
      const resp = await fetchAutoresponder(slug);
      setAr(resp.autoresponder);
      setArEnabled(resp.autoresponder.enabled);
      setArSubject(resp.autoresponder.subject);
      setArBody(resp.autoresponder.body);
      setArReplyField(resp.autoresponder.reply_field || "email");
      setArState("saved");
      setTimeout(() => setArState("idle"), 2000);
    } catch (e) {
      setArError(e instanceof Error ? e.message : String(e));
      setArState("error");
    }
  }

  if (loading) {
    return (
      <div className="p-8 text-center text-muted-foreground">
        Loading settings…
      </div>
    );
  }

  return (
    <div className="max-w-2xl space-y-10">
      <header className="space-y-2">
        <p className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
          Inbox settings · {slug}
        </p>
        <h1 className="font-display text-3xl font-bold text-foreground">
          Outbound delivery
        </h1>
        <p className="text-sm text-muted-foreground">
          Decide what happens after a visitor submits your contact form.
          Both options are optional; the inbox keeps every submission
          regardless.
        </p>
      </header>

      {/* --- Webhook section --- */}
      <section className="space-y-4 bg-card border border-border rounded-2xl p-6">
        <div className="space-y-1">
          <h2 className="font-display text-xl font-bold text-foreground">
            Webhook URL
          </h2>
          <p className="text-sm text-muted-foreground">
            We POST each submission as JSON to this URL. Use a Zapier,
            Make, Slack, or HubSpot incoming-webhook URL to forward
            leads to your tools.
          </p>
        </div>

        <label className="block space-y-2">
          <span className="text-sm font-medium text-foreground">URL</span>
          <input
            type="url"
            inputMode="url"
            value={webhookUrl}
            onChange={(e) => setWebhookUrl(e.target.value)}
            placeholder="https://hooks.zapier.com/hooks/catch/..."
            className="w-full rounded-xl border border-border bg-background px-4 py-3 text-base text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </label>

        {webhook && (
          <p className="text-xs text-muted-foreground">
            Configured {new Date(webhook.configured_at).toLocaleString()}
          </p>
        )}

        {webhookError && (
          <p role="alert" className="text-sm text-destructive">{webhookError}</p>
        )}

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={saveWebhook}
            disabled={webhookState === "saving" || !webhookUrl.trim()}
            className="inline-flex items-center justify-center rounded-full bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed transition-transform"
          >
            {webhookState === "saving" ? "Saving…" : webhookState === "saved" ? "Saved" : "Save URL"}
          </button>
          {webhook && (
            <button
              onClick={removeWebhook}
              disabled={webhookState === "saving"}
              className="text-sm text-muted-foreground hover:text-destructive px-3 py-2 rounded-lg hover:bg-destructive/10 disabled:opacity-50"
            >
              Remove
            </button>
          )}
        </div>
      </section>

      {/* --- Autoresponder section --- */}
      <section className="space-y-4 bg-card border border-border rounded-2xl p-6">
        <div className="space-y-1">
          <h2 className="font-display text-xl font-bold text-foreground">
            Auto-reply to submitters
          </h2>
          <p className="text-sm text-muted-foreground">
            When a visitor submits the form with an email address,
            send them a branded thank-you so they know it landed.
            Use{" "}
            <code className="font-mono text-foreground">{"{{ field_name }}"}</code>{" "}
            anywhere in the subject or body to drop in what they typed
            (e.g. <code className="font-mono text-foreground">{"{{ name }}"}</code>).
          </p>
        </div>

        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={arEnabled}
            onChange={(e) => setArEnabled(e.target.checked)}
            className="h-4 w-4 rounded border-border"
          />
          <span className="text-sm font-medium text-foreground">
            Send auto-reply when a submission has an email field
          </span>
        </label>

        <label className="block space-y-2">
          <span className="text-sm font-medium text-foreground">Subject</span>
          <input
            type="text"
            value={arSubject}
            onChange={(e) => setArSubject(e.target.value)}
            maxLength={200}
            disabled={!arEnabled}
            className="w-full rounded-xl border border-border bg-background px-4 py-3 text-base text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
          />
        </label>

        <label className="block space-y-2">
          <span className="text-sm font-medium text-foreground">Body</span>
          <textarea
            value={arBody}
            onChange={(e) => setArBody(e.target.value)}
            rows={8}
            maxLength={8192}
            disabled={!arEnabled}
            className="w-full rounded-xl border border-border bg-background px-4 py-3 text-base text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50 font-mono text-sm"
          />
          <span className="text-xs text-muted-foreground">
            Plain text. {arBody.length} / 8192 chars.
          </span>
        </label>

        <label className="block space-y-2">
          <span className="text-sm font-medium text-foreground">
            Recipient field name
          </span>
          <input
            type="text"
            value={arReplyField}
            onChange={(e) => setArReplyField(e.target.value)}
            disabled={!arEnabled}
            placeholder="email"
            className="w-full rounded-xl border border-border bg-background px-4 py-3 text-base text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50 font-mono"
          />
          <span className="text-xs text-muted-foreground">
            The form field that holds the visitor's email address.
            Default <code className="font-mono">email</code>.
          </span>
        </label>

        {arError && (
          <p role="alert" className="text-sm text-destructive">{arError}</p>
        )}

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={saveAr}
            disabled={arState === "saving"}
            className="inline-flex items-center justify-center rounded-full bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed transition-transform"
          >
            {arState === "saving" ? "Saving…" : arState === "saved" ? "Saved" : "Save"}
          </button>
          {ar && ar.configured_at && (
            <button
              onClick={resetAr}
              disabled={arState === "saving"}
              className="text-sm text-muted-foreground hover:text-destructive px-3 py-2 rounded-lg hover:bg-destructive/10 disabled:opacity-50"
            >
              Reset to defaults
            </button>
          )}
        </div>

        <details className="text-xs text-muted-foreground">
          <summary className="cursor-pointer">How throttling works</summary>
          <div className="mt-2 space-y-1 pl-4">
            <p>· At most one auto-reply per recipient email per hour.</p>
            <p>· At most 50 auto-replies per project per 24 hours (spam-cannon protection).</p>
            <p>· If a visitor submits twice within an hour, only the first triggers an auto-reply.</p>
          </div>
        </details>
      </section>
    </div>
  );
}
