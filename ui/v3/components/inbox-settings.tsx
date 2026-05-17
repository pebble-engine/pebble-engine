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
import { useRouter } from "next/navigation";
import {
  fetchWebhookConfig,
  setWebhookConfig,
  clearWebhookConfig,
  fetchAutoresponder,
  saveAutoresponder,
  clearAutoresponder,
  deleteAccount,
  type WebhookConfig,
  type AutoresponderConfig,
} from "@/lib/api";
import { createClient } from "@/lib/supabase/client";
import { useAuth } from "@/components/auth-provider";

type SaveState = "idle" | "saving" | "saved" | "error";

export function InboxSettings({ slug }: { slug: string }) {
  const router = useRouter();
  const { user } = useAuth();

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

  // ---- Account-delete (GDPR Ch 7.7) state ----
  const [deleteState, setDeleteState] = useState<SaveState>("idle");
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [confirmText, setConfirmText] = useState("");

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      // Settle each fetch independently so a failure on one config
      // doesn't take the other section down with it. NLM round on
      // Tracks 9–11 flagged the previous Promise.all-then-catch
      // pattern as a state-desync T3 (autoresponder section would
      // hang in loading state when only webhook failed).
      const results = await Promise.allSettled([
        fetchWebhookConfig(slug),
        fetchAutoresponder(slug),
      ]);
      if (cancelled) return;
      const [whResult, arResult] = results;
      if (whResult.status === "fulfilled") {
        setWebhook(whResult.value.webhook);
        setWebhookUrl(whResult.value.webhook?.url || "");
      } else {
        const err = whResult.reason;
        setWebhookError(err instanceof Error ? err.message : String(err));
      }
      if (arResult.status === "fulfilled") {
        setAr(arResult.value.autoresponder);
        setArEnabled(arResult.value.autoresponder.enabled);
        setArSubject(arResult.value.autoresponder.subject);
        setArBody(arResult.value.autoresponder.body);
        setArReplyField(arResult.value.autoresponder.reply_field || "email");
      } else {
        const err = arResult.reason;
        setArError(err instanceof Error ? err.message : String(err));
      }
      setLoading(false);
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

  async function onDeleteAccount() {
    // Two-step gate: typed EMAIL match + browser confirm.
    //
    // NLM round on Track 12 flagged the previous "type DELETE"
    // pattern as a defense-in-depth gap: an unattended-computer
    // attacker would only need to type the literal word "DELETE"
    // to wipe the account. Requiring the user's full email defeats
    // that — an attacker has to either know it or look it up
    // (and if they have THAT level of access, they could already
    // log in as the user via password reset).
    const expectedEmail = (user?.email || "").trim().toLowerCase();
    if (!expectedEmail) {
      setDeleteError("You must be signed in to delete your account.");
      return;
    }
    if (confirmText.trim().toLowerCase() !== expectedEmail) {
      setDeleteError(`Type your email address exactly (${expectedEmail}) to confirm.`);
      return;
    }
    if (!confirm(
      "This will PERMANENTLY delete your account, all projects, and " +
      "any submissions. There is no undo. Proceed?"
    )) {
      return;
    }
    setDeleteState("saving");
    setDeleteError(null);
    try {
      const result = await deleteAccount();
      // Server-side delete succeeded. Now scrub client cookies via
      // Supabase's signOut. Then route to /landing.
      try {
        const supabase = createClient();
        await supabase.auth.signOut();
      } catch {
        // signOut errors are non-fatal — the cookies will expire on
        // their own and the server-side account is already gone.
      }
      router.push(result.next || "/landing");
    } catch (e) {
      setDeleteError(e instanceof Error ? e.message : String(e));
      setDeleteState("error");
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

      {/* --- Danger zone (Ch 7.7 GDPR delete) ---
        * Lives at the bottom of inbox-settings for now since no
        * dedicated /settings page exists yet. The action is per-USER
        * (not per-project), so when the /settings page lands this
        * section should move there.
        */}
      <section className="space-y-4 bg-card border-2 border-destructive/40 rounded-2xl p-6">
        <div className="space-y-1">
          <h2 className="font-display text-xl font-bold text-destructive">
            Danger zone
          </h2>
          <p className="text-sm text-muted-foreground">
            Permanently delete your Pebble account. This wipes your
            login, all projects, every submission in every inbox, and
            removes your data from our records. <strong>There is no
            undo.</strong>
          </p>
        </div>

        <label className="block space-y-2">
          <span className="text-sm font-medium text-foreground">
            Type your email{" "}
            {user?.email && (
              <code className="font-mono text-destructive">{user.email}</code>
            )}{" "}
            below to confirm
          </span>
          <input
            type="email"
            value={confirmText}
            onChange={(e) => setConfirmText(e.target.value)}
            placeholder={user?.email || "your-email@example.com"}
            autoComplete="off"
            spellCheck={false}
            className="w-full rounded-xl border border-border bg-background px-4 py-3 text-base text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-destructive font-mono"
          />
        </label>

        {deleteError && (
          <p role="alert" className="text-sm text-destructive">{deleteError}</p>
        )}

        <button
          onClick={onDeleteAccount}
          disabled={
            deleteState === "saving" ||
            !user?.email ||
            confirmText.trim().toLowerCase() !== user.email.trim().toLowerCase()
          }
          className="inline-flex items-center justify-center rounded-full bg-destructive px-5 py-2.5 text-sm font-medium text-destructive-foreground hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed transition-transform"
        >
          {deleteState === "saving" ? "Deleting account…" : "Delete my account permanently"}
        </button>

        <p className="text-xs text-muted-foreground">
          You'll be signed out and returned to the landing page. We
          honour this request within seconds — your auth row, profile
          row, and all linked data are removed in one go.
        </p>
      </section>
    </div>
  );
}
