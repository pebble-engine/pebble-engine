"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Share2, Eye, Edit3, Droplet, Download, Rocket, Check, Globe, Trash2, Copy } from "lucide-react";
import {
  publishSite,
  fetchDomain,
  setDomain,
  removeDomain,
  type PublishResponse,
  type DomainResponse,
} from "@/lib/api";

/**
 * Publish phase — the final step of the build journey. Renders inside
 * the unified workspace shell as ``phase=publish`` instead of being
 * its own route. Internal state machine:
 *
 *   ready → publishing → done | error
 *
 * "Keep editing" calls ``onBack()``, which the shell wires to flip
 * back to the design phase without a route change. "Try again" from
 * the error state retries the publish call in place.
 */

type InternalPhase = "ready" | "publishing" | "done" | "error";

type Props = {
  build: { slug: string; preview_url: string } | null;
  onBack: () => void;
};

export function PublishPhase({ build, onBack }: Props) {
  const [phase, setPhase] = useState<InternalPhase>("ready");
  const [result, setResult] = useState<PublishResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [shareLabel, setShareLabel] = useState("Share");

  // If the shell ever lands here without a build (e.g. user types
  // /workspace#phase=publish into the address bar before generating
  // anything), the parent shell bootstrap snaps them back to welcome.
  // No additional guard needed here beyond a defensive null check.

  async function handlePublish() {
    if (!build?.slug) return;
    setPhase("publishing");
    setError(null);
    try {
      const r = await publishSite(build.slug, "auto");
      setResult(r);
      setPhase("done");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Publish failed.");
      setPhase("error");
    }
  }

  function handleShare() {
    if (!result?.url) return;
    const absolute = result.url.startsWith("http") ? result.url : `${window.location.origin}${result.url}`;
    navigator.clipboard?.writeText(absolute);
    setShareLabel("Copied!");
    setTimeout(() => setShareLabel("Share"), 1500);
  }

  const previewUrl = build?.preview_url || "#";

  return (
    <main className="flex-1 overflow-y-auto flex flex-col items-center justify-center px-4 py-16">
      <motion.div
        initial={{ scale: 0.4, opacity: 0, rotate: -8 }}
        animate={{ scale: 1, opacity: 1, rotate: 0 }}
        transition={{ duration: 0.8, ease: [0.4, 0, 0.2, 1] }}
        className="mb-10 text-primary relative"
      >
        <div className="pebble-ripple absolute -inset-12 flex items-center justify-center" />
        <Droplet className="w-12 h-12 fill-current relative z-10" strokeWidth={1.5} />
      </motion.div>

      <motion.div
        initial="hidden"
        animate="visible"
        variants={{ hidden: {}, visible: { transition: { staggerChildren: 0.1 } } }}
        className="max-w-2xl w-full text-center space-y-10"
      >
        {phase === "ready" && <ReadyPanel onPublish={handlePublish} previewUrl={previewUrl} />}
        {phase === "publishing" && <PublishingPanel />}
        {phase === "done" && result && (
          <>
            <DonePanel
              result={result}
              previewUrl={previewUrl}
              shareLabel={shareLabel}
              onShare={handleShare}
              onKeepEditing={onBack}
            />
            <DomainPanel slug={build?.slug || ""} />
          </>
        )}
        {phase === "error" && (
          <ErrorPanel
            error={error || "Something went wrong."}
            onRetry={handlePublish}
            onBack={onBack}
          />
        )}
      </motion.div>
    </main>
  );
}

// ---------------------------------------------------------------------------

function ReadyPanel({ onPublish, previewUrl }: { onPublish: () => void; previewUrl: string }) {
  return (
    <>
      <motion.h1
        variants={{ hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0 } }}
        transition={{ duration: 0.5 }}
        className="font-display text-5xl md:text-6xl font-bold tracking-tight text-foreground"
      >
        Ready to publish?
      </motion.h1>
      <motion.div
        variants={{ hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0 } }}
        transition={{ duration: 0.5 }}
        className="bg-card border border-border rounded-2xl p-8 md:p-10 shadow-[var(--shadow-1)] space-y-6"
      >
        <p className="text-muted-foreground">
          We&apos;ll bundle your site into a deployable archive. If you&apos;ve added Cloudflare keys, we&apos;ll
          push it live to a public URL. Otherwise you&apos;ll get a download you can drop into any host.
        </p>
        <div className="flex gap-3 justify-center">
          <motion.button
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.97 }}
            onClick={onPublish}
            className="bg-primary text-primary-foreground px-7 py-3 rounded-full font-bold flex items-center gap-2 hover:opacity-90"
          >
            <Rocket className="w-4 h-4" /> Publish now
          </motion.button>
          <a
            href={previewUrl}
            target="_blank"
            rel="noopener"
            className="bg-card border border-border text-foreground px-6 py-3 rounded-full font-semibold flex items-center gap-2 hover:bg-accent"
          >
            <Eye className="w-4 h-4" /> Preview first
          </a>
        </div>
      </motion.div>
    </>
  );
}

function PublishingPanel() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-card border border-border rounded-2xl p-12 shadow-[var(--shadow-1)] space-y-6"
    >
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 1.6, repeat: Infinity, ease: "linear" }}
        className="w-12 h-12 mx-auto rounded-full border-4 border-primary border-t-transparent"
      />
      <p className="font-display text-2xl text-foreground">Packaging your site…</p>
      <p className="text-muted-foreground text-sm">Snapshotting, bundling, and verifying. Usually a few seconds.</p>
    </motion.div>
  );
}

function DonePanel({
  result,
  previewUrl,
  shareLabel,
  onShare,
  onKeepEditing,
}: {
  result: PublishResponse;
  previewUrl: string;
  shareLabel: string;
  onShare: () => void;
  onKeepEditing: () => void;
}) {
  const isLive = result.kind === "cloudflare";
  const fullUrl = result.url.startsWith("http")
    ? result.url
    : typeof window !== "undefined" ? `${window.location.origin}${result.url}` : result.url;

  return (
    <>
      <motion.h1
        variants={{ hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0 } }}
        transition={{ duration: 0.5 }}
        className="font-display text-5xl md:text-6xl font-bold tracking-tight text-foreground"
      >
        {isLive ? "Your website is live." : "Your site is packaged."}
      </motion.h1>
      <motion.div
        variants={{ hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0 } }}
        transition={{ duration: 0.5 }}
        className="bg-card border border-border rounded-2xl p-8 md:p-10 shadow-[var(--shadow-1)] space-y-8"
      >
        <div className="flex flex-col items-center">
          <div className="bg-accent border border-border rounded-lg px-6 py-3 mb-3 flex items-center gap-3 max-w-full">
            <span className="font-mono text-base tracking-tight text-primary truncate">{fullUrl}</span>
          </div>
          <p className="text-muted-foreground text-xs font-bold uppercase tracking-widest">
            {isLive ? "URL active" : `${result.files_published} files · ${formatBytes(result.bytes_published)}`}
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-6 border-t border-border">
          <ActionButton onClick={onShare} icon={shareLabel === "Copied!" ? Check : Share2} label={shareLabel} />
          {isLive ? (
            <ActionLink href={fullUrl} icon={Eye} label="View as visitor" />
          ) : (
            <ActionLink href={result.url} icon={Download} label="Download ZIP" download />
          )}
          <ActionButton onClick={onKeepEditing} icon={Edit3} label="Keep editing" />
        </div>
      </motion.div>

      {result.note && (
        <motion.p
          variants={{ hidden: { opacity: 0 }, visible: { opacity: 1 } }}
          className="text-muted-foreground text-sm leading-relaxed max-w-md mx-auto"
        >
          {result.note}
        </motion.p>
      )}

      {result.cloudflare_setup_md && (
        <details className="bg-card border border-border rounded-xl text-left p-5 max-w-xl mx-auto">
          <summary className="font-semibold text-foreground cursor-pointer text-sm">
            Want a live URL on Cloudflare? Set it up (5 min)
          </summary>
          <pre className="whitespace-pre-wrap font-mono text-xs text-muted-foreground mt-4 leading-relaxed">
            {result.cloudflare_setup_md}
          </pre>
        </details>
      )}

      <motion.p
        variants={{ hidden: { opacity: 0 }, visible: { opacity: 1 } }}
        className="text-muted-foreground"
      >
        Everything is editable later. You don&apos;t have to be done.
      </motion.p>
    </>
  );
}

function ErrorPanel({ error, onRetry, onBack }: { error: string; onRetry: () => void; onBack: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card border border-destructive/40 rounded-2xl p-8 space-y-5"
    >
      <p className="font-display text-2xl text-foreground">Publish hit a snag.</p>
      <p className="text-sm text-muted-foreground font-mono break-words">{error}</p>
      <div className="flex gap-3 justify-center">
        <button
          onClick={onRetry}
          className="bg-primary text-primary-foreground px-5 py-2.5 rounded-full font-bold hover:opacity-90"
        >
          Try again
        </button>
        <button
          onClick={onBack}
          className="bg-card border border-border text-foreground px-5 py-2.5 rounded-full font-semibold hover:bg-accent"
        >
          Back to workspace
        </button>
      </div>
    </motion.div>
  );
}

function ActionButton({ onClick, icon: Icon, label }: { onClick: () => void; icon: typeof Share2; label: string }) {
  return (
    <motion.button
      onClick={onClick}
      whileHover={{ y: -2 }}
      whileTap={{ scale: 0.96 }}
      className="flex flex-col items-center gap-3 p-4 rounded-lg hover:bg-accent transition-colors group"
    >
      <div className="w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center group-hover:scale-105 transition-transform">
        <Icon className="w-5 h-5" />
      </div>
      <span className="text-sm font-semibold">{label}</span>
    </motion.button>
  );
}

function ActionLink({
  href, icon: Icon, label, download,
}: { href: string; icon: typeof Share2; label: string; download?: boolean }) {
  return (
    <motion.a
      href={href}
      target={download ? undefined : "_blank"}
      rel="noopener"
      download={download}
      whileHover={{ y: -2 }}
      whileTap={{ scale: 0.96 }}
      className="flex flex-col items-center gap-3 p-4 rounded-lg hover:bg-accent transition-colors group"
    >
      <div className="w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center group-hover:scale-105 transition-transform">
        <Icon className="w-5 h-5" />
      </div>
      <span className="text-sm font-semibold">{label}</span>
    </motion.a>
  );
}

function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / 1024 / 1024).toFixed(2)} MB`;
}

// ---------------------------------------------------------------------------
// DomainPanel — collapsed by default; expands into the attach/detach UI.
// ---------------------------------------------------------------------------

function DomainPanel({ slug }: { slug: string }) {
  const [open, setOpen] = useState(false);
  const [state, setState] = useState<DomainResponse | null>(null);
  const [host, setHost] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!open || !slug) return;
    fetchDomain(slug).then(setState).catch(() => setState(null));
  }, [open, slug]);

  async function handleAttach() {
    if (!host.trim() || !slug) return;
    setBusy(true); setError(null);
    try {
      const next = await setDomain(slug, host.trim());
      setState(next);
      setHost("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Domain attach failed.");
    } finally {
      setBusy(false);
    }
  }

  async function handleDetach() {
    if (!slug || !state?.domain) return;
    setBusy(true); setError(null);
    try {
      await removeDomain(slug);
      setState({ ...state, domain: null });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Domain detach failed.");
    } finally {
      setBusy(false);
    }
  }

  function copyCname() {
    if (!state?.domain) return;
    navigator.clipboard?.writeText(state.domain.cname_record);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <details
      onToggle={(e) => setOpen((e.currentTarget as HTMLDetailsElement).open)}
      className="bg-card border border-border rounded-2xl max-w-xl mx-auto text-left p-5"
    >
      <summary className="font-display text-lg font-semibold text-foreground cursor-pointer flex items-center gap-2">
        <Globe className="w-4 h-4 text-primary" />
        Connect a custom domain
      </summary>

      <div className="mt-5 space-y-4">
        {state?.cloudflare_configured === false && (
          <div className="text-xs bg-muted text-muted-foreground rounded-lg p-3">
            Cloudflare keys aren&apos;t configured yet. You can still save your domain — it&apos;ll
            activate as soon as Cloudflare is wired up.
          </div>
        )}

        {state?.domain ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between gap-3">
              <div className="min-w-0">
                <p className="font-mono text-base text-foreground truncate">{state.domain.host}</p>
                <p className="text-xs uppercase tracking-widest mt-1 font-bold">
                  <span className={
                    state.domain.status === "active"
                      ? "text-spark"
                      : state.domain.status === "error"
                        ? "text-destructive"
                        : "text-muted-foreground"
                  }>
                    {state.domain.status === "active"
                      ? "Live"
                      : state.domain.status === "error"
                        ? "Error — check DNS"
                        : "DNS pending"}
                  </span>
                </p>
              </div>
              <button
                onClick={handleDetach}
                disabled={busy}
                className="bg-card border border-border text-muted-foreground hover:text-destructive hover:border-destructive/40 px-3 py-1.5 rounded-lg text-sm font-semibold flex items-center gap-1 disabled:opacity-50"
              >
                <Trash2 className="w-3 h-3" /> Remove
              </button>
            </div>

            <div className="bg-background border border-border rounded-lg p-3 space-y-2">
              <p className="text-xs uppercase font-bold tracking-widest text-muted-foreground">
                Add this DNS record at your domain host
              </p>
              <div className="flex items-center gap-2">
                <code className="font-mono text-xs flex-1 truncate text-foreground">{state.domain.cname_record}</code>
                <button
                  onClick={copyCname}
                  className="bg-card border border-border px-2 py-1 rounded text-xs hover:bg-accent flex items-center gap-1"
                >
                  {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                  {copied ? "Copied" : "Copy"}
                </button>
              </div>
              <p className="text-[11px] text-muted-foreground leading-relaxed">
                After saving the record at GoDaddy / Namecheap / Cloudflare DNS / wherever, it can take
                a few minutes to propagate. We&apos;ll show <span className="text-spark font-semibold">Live</span> automatically.
              </p>
            </div>

            {state.domain.error && (
              <p className="text-xs text-destructive">{state.domain.error}</p>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground">
              Connect your existing domain (like <span className="font-mono text-foreground">yourbiz.com</span>)
              so visitors don&apos;t see the default Pebble URL.
            </p>
            <div className="flex gap-2">
              <input
                value={host}
                onChange={(e) => setHost(e.target.value)}
                placeholder="example.com"
                className="flex-1 bg-background border border-border rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-ring"
                disabled={busy}
              />
              <button
                onClick={handleAttach}
                disabled={busy || !host.trim()}
                className="bg-primary text-primary-foreground px-4 py-2 rounded-lg text-sm font-semibold hover:opacity-90 disabled:opacity-40"
              >
                {busy ? "Saving…" : "Connect"}
              </button>
            </div>
            {error && <p className="text-xs text-destructive">{error}</p>}
          </div>
        )}
      </div>
    </details>
  );
}
