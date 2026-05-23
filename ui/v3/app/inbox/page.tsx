"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { Mail, Trash2, MailOpen, Inbox as InboxIcon, ArrowLeft, RefreshCw, Settings } from "lucide-react";
import { TopNav } from "@/components/top-nav";
import { InboxSettings } from "@/components/inbox-settings";
import {
  fetchInbox,
  fetchAttachmentSignedUrl,
  markSubmissionRead,
  deleteSubmission,
  type Submission,
} from "@/lib/api";

function InboxForSlug({ slug }: { slug: string }) {
  const router = useRouter();
  const [items, setItems] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Submission | null>(null);
  const [view, setView] = useState<"submissions" | "settings">("submissions");
  // Surface a one-line error banner. Previously every fetch error was
  // swallowed with `catch {}` — meaning a 401 / 500 / network blip
  // would silently revert the UI to its old state (e.g. a "deleted"
  // item re-appears after refresh) and look like a ghost bug. Now we
  // tell the user what happened so they can retry or escalate.
  const [opError, setOpError] = useState<string | null>(null);

  async function refresh() {
    setLoading(true);
    try {
      const r = await fetchInbox(slug);
      setItems(r.submissions);
    } catch (e) {
      setOpError(e instanceof Error ? `Failed to load inbox: ${e.message}` : "Failed to load inbox");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void refresh(); /* eslint-disable-next-line */ }, [slug]);

  async function open(sub: Submission) {
    setSelected(sub);
    if (!sub.read) {
      try {
        await markSubmissionRead(slug, sub.id, true);
        refresh();
      } catch (e) {
        setOpError(e instanceof Error
          ? `Couldn't mark as read: ${e.message}`
          : "Couldn't mark as read");
      }
    }
  }

  async function remove(sub: Submission) {
    if (!confirm("Delete this submission?")) return;
    try {
      await deleteSubmission(slug, sub.id);
      setSelected(null);
      refresh();
    } catch (e) {
      setOpError(e instanceof Error
        ? `Couldn't delete: ${e.message}`
        : "Couldn't delete this submission");
    }
  }

  return (
    <div className="flex flex-1 overflow-hidden flex-col">
      {/* Error banner — only renders when an inbox operation failed.
          Dismissible. Sits above the columns so the user sees it
          regardless of which pane they're looking at. */}
      {opError && (
        <div className="bg-amber-50 border-b border-amber-200 text-amber-900 px-4 py-2 text-sm flex items-center justify-between">
          <span>{opError}</span>
          <button
            onClick={() => setOpError(null)}
            className="text-amber-700 hover:text-amber-900 font-semibold ml-4"
            aria-label="Dismiss error"
          >
            ×
          </button>
        </div>
      )}
    <div className="flex flex-1 overflow-hidden">
      <aside className="w-[360px] border-r border-border bg-card flex flex-col">
        <div className="p-4 border-b border-border flex items-center justify-between">
          <button
            onClick={() => router.push("/dashboard")}
            className="text-sm font-semibold text-muted-foreground hover:text-foreground flex items-center gap-1"
          >
            <ArrowLeft className="w-4 h-4" /> Dashboard
          </button>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setView(view === "settings" ? "submissions" : "settings")}
              className={`w-8 h-8 rounded-full hover:bg-accent flex items-center justify-center ${
                view === "settings" ? "bg-accent text-foreground" : "text-muted-foreground"
              }`}
              aria-label={view === "settings" ? "Back to submissions" : "Inbox settings"}
              title={view === "settings" ? "Back to submissions" : "Inbox settings"}
            >
              <Settings className="w-4 h-4" />
            </button>
            <button
              onClick={() => refresh()}
              className="w-8 h-8 rounded-full hover:bg-accent flex items-center justify-center"
              aria-label="Refresh"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            </button>
          </div>
        </div>
        <div className="p-4 border-b border-border">
          <p className="text-xs font-mono uppercase tracking-widest text-muted-foreground">Inbox</p>
          <p className="font-display text-xl font-bold text-foreground truncate">{slug}</p>
          <p className="text-xs text-muted-foreground mt-1">{items.length} submission{items.length === 1 ? "" : "s"}</p>
        </div>
        <div className="flex-1 overflow-y-auto">
          {items.length === 0 && !loading && (
            <div className="text-center py-12 px-4">
              <InboxIcon className="w-8 h-8 mx-auto text-muted-foreground mb-3" />
              <p className="text-sm text-muted-foreground">Nothing here yet.</p>
              <p className="text-xs text-muted-foreground mt-2">
                Submissions to <code className="font-mono text-foreground">POST /api/forms/{slug}</code> land here.
              </p>
            </div>
          )}
          {items.map((sub) => (
            <button
              key={sub.id}
              onClick={() => open(sub)}
              className={`w-full text-left p-4 border-b border-border hover:bg-accent transition-colors ${
                selected?.id === sub.id ? "bg-accent" : ""
              }`}
            >
              <div className="flex items-start gap-2">
                {sub.read ? (
                  <MailOpen className="w-4 h-4 text-muted-foreground mt-0.5 shrink-0" />
                ) : (
                  <Mail className="w-4 h-4 text-primary mt-0.5 shrink-0" />
                )}
                <div className="min-w-0 flex-1">
                  <p className={`text-sm truncate ${sub.read ? "font-normal" : "font-semibold"} text-foreground`}>
                    {previewLine(sub)}
                  </p>
                  <p className="text-[11px] text-muted-foreground mt-0.5">
                    {formatRelative(sub.received_at)}
                  </p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </aside>

      <main className="flex-1 p-8 overflow-y-auto">
        {view === "settings" ? (
          <InboxSettings slug={slug} />
        ) : !selected ? (
          <div className="h-full flex flex-col items-center justify-center text-center text-muted-foreground gap-2">
            <InboxIcon className="w-10 h-10 mb-2 opacity-50" />
            <p className="font-display text-xl text-foreground">Pick a submission</p>
            <p className="text-sm">{items.length === 0 ? "There aren't any yet." : "Click one on the left."}</p>
          </div>
        ) : (
          <AnimatePresence mode="wait">
            <motion.div
              key={selected.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              transition={{ duration: 0.25 }}
              className="max-w-2xl space-y-6"
            >
              <div className="flex items-center justify-between gap-2">
                <p className="text-xs font-mono text-muted-foreground">
                  {new Date(selected.received_at).toLocaleString()}
                </p>
                <button
                  onClick={() => remove(selected)}
                  className="text-sm text-muted-foreground hover:text-destructive flex items-center gap-1 px-3 py-1.5 rounded-lg hover:bg-destructive/10"
                >
                  <Trash2 className="w-3 h-3" /> Delete
                </button>
              </div>

              <dl className="space-y-4 bg-card border border-border rounded-2xl p-6">
                {Object.entries(selected.fields).map(([k, v]) => (
                  <div key={k}>
                    <dt className="text-xs font-bold uppercase tracking-widest text-muted-foreground">
                      {k.replace(/_/g, " ")}
                    </dt>
                    <dd className="mt-1 text-foreground whitespace-pre-wrap break-words">
                      <FieldValue slug={slug} raw={String(v)} />
                    </dd>
                  </div>
                ))}
              </dl>

              <details className="text-xs text-muted-foreground">
                <summary className="cursor-pointer hover:text-foreground">Headers (for support diagnostics)</summary>
                <div className="mt-2 font-mono space-y-1">
                  {selected.user_agent && <p>UA: {selected.user_agent}</p>}
                  {selected.referrer && <p>Referer: {selected.referrer}</p>}
                  {selected.ip_hash && <p>IP hash: {selected.ip_hash}</p>}
                </div>
              </details>
            </motion.div>
          </AnimatePresence>
        )}
      </main>
    </div>
    </div>
  );
}

/**
 * FieldValue — render one submission field's value. Most fields are
 * plain text; a value that looks like a Supabase Storage URL or a
 * stored-attachment path gets a "Download attachment" button that
 * fetches a short-lived signed URL on click (the bucket is private).
 *
 * Detection rules (deliberately conservative):
 *   1. Starts with `https://<host>.supabase.co/storage/v1/object/`,
 *      contains `/<slug>/`, looks like a Supabase Storage URL.
 *   2. Starts with `<slug>/` and ends in a known file extension —
 *      treated as a bare object path (the upload endpoint's response
 *      shape).
 *
 * If neither pattern matches, render as plain text.
 */
function FieldValue({ slug, raw }: { slug: string; raw: string }) {
  const value = (raw || "").trim();

  // Path-shape: "<slug>/<nonce>/<filename.ext>"
  const looksLikePath =
    value.startsWith(`${slug}/`) &&
    /\.(jpe?g|png|gif|webp|heic|heif|pdf|txt|docx?|md)$/i.test(value) &&
    !value.includes("\n") &&
    value.length < 512;

  // URL-shape: a public Supabase Storage URL pointing at the same slug.
  const urlMatch = !looksLikePath &&
    /^https:\/\/[a-z0-9-]+\.supabase\.co\/storage\/v1\/object\/(public|sign)\/[^/]+\//i.test(value) &&
    value.includes(`/${slug}/`);

  const path = looksLikePath
    ? value
    : urlMatch
    ? value.substring(value.indexOf(`/${slug}/`) + 1)  // strip everything up to and including "/"
    : null;

  if (!path) {
    return <>{raw}</>;
  }

  const filename = path.split("/").pop() || path;
  return <AttachmentLink slug={slug} path={path} label={filename} />;
}

function AttachmentLink({ slug, path, label }: { slug: string; path: string; label: string }) {
  const [opening, setOpening] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function openAttachment() {
    setOpening(true);
    setError(null);
    try {
      const { url } = await fetchAttachmentSignedUrl(slug, path);
      window.open(url, "_blank", "noopener,noreferrer");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setOpening(false);
    }
  }

  return (
    <span className="inline-flex flex-col items-start gap-1">
      <button
        onClick={openAttachment}
        disabled={opening}
        className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-3 py-1.5 text-sm font-medium text-foreground hover:bg-accent disabled:opacity-50 transition-colors"
        title={path}
      >
        <svg viewBox="0 0 24 24" className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2}>
          <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
        {opening ? "Opening…" : `Download ${label}`}
      </button>
      {error && <span className="text-xs text-destructive">{error}</span>}
    </span>
  );
}

function previewLine(sub: Submission): string {
  const f = sub.fields || {};
  if (f.name || f.email) return [f.name, f.email].filter(Boolean).join(" · ");
  const first = Object.values(f)[0];
  return first ? String(first).slice(0, 80) : sub.id;
}

function formatRelative(iso: string): string {
  if (!iso) return "";
  try {
    const t = new Date(iso).getTime();
    if (Number.isNaN(t)) return iso;
    const seconds = Math.floor((Date.now() - t) / 1000);
    if (seconds < 60)    return "just now";
    if (seconds < 3600)  return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  } catch { return iso; }
}

function InboxRoute() {
  const params = useSearchParams();
  const slug = params.get("slug") || "";
  if (!slug) {
    return (
      <div className="flex-1 flex items-center justify-center text-center px-6">
        <div className="max-w-md space-y-3">
          <InboxIcon className="w-10 h-10 mx-auto text-muted-foreground" />
          <h1 className="font-display text-3xl text-foreground">Pick a project</h1>
          <p className="text-muted-foreground text-sm">
            Open any project from the <Link href="/dashboard" className="text-primary hover:underline">dashboard</Link>;
            its inbox shows submissions to its contact form.
          </p>
        </div>
      </div>
    );
  }
  return <InboxForSlug slug={slug} />;
}

export default function InboxPage() {
  return (
    <div className="min-h-screen-safe flex flex-col">
      <TopNav projectName="Inbox" />
      <Suspense fallback={<div className="flex-1 flex items-center justify-center text-muted-foreground">Loading…</div>}>
        <InboxRoute />
      </Suspense>
    </div>
  );
}
