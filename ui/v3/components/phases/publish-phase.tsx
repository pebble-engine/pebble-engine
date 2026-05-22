"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { STANDARD_S, SHORT_S, SLOW_S, EASE_CINEMATIC, EASE_QUIET } from "@/lib/motion";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";
import { Share2, Eye, Edit3, Droplet, Download, Rocket, Check, Globe, Trash2, Copy } from "lucide-react";
import {
  publishSite,
  publishInstant,
  fetchDomain,
  setDomain,
  removeDomain,
  pickPreviewUrl,
  PlanLimitError,
  type PublishResponse,
  type InstantPublishResponse,
  type DomainResponse,
  type DevServerInfo,
} from "@/lib/api";

/**
 * Publish phase — Phase 44 (2026-05-22) instant subdomain rework.
 *
 * The default "Publish" button now calls /api/publish/instant — the
 * engine flips a sentinel and ``<slug>.pebbleapp.ai`` is live in a
 * single round-trip (no Cloudflare upload = no 30s wait, matching
 * Base44's killer UX moment).
 *
 * Internal state machine:
 *
 *   ready → publishing → done | error
 *
 * On success we surface the public URL prominently with copy + native
 * share + social-share shortcuts. A confetti burst marks the moment so
 * "I just published a website" registers as a real event.
 *
 * Legacy ZIP / Cloudflare publish is collapsed into a "Need advanced
 * options?" details block below — power-user escape hatch when someone
 * wants a custom domain or a downloadable archive instead of the
 * subdomain.
 */

type InternalPhase = "ready" | "publishing" | "done" | "error";
type DoneResult =
  | { mode: "instant";  data: InstantPublishResponse }
  | { mode: "advanced"; data: PublishResponse };

type Props = {
  build: {
    slug: string;
    preview_url: string;
    dev_server?: DevServerInfo | null;
  } | null;
  onBack: () => void;
};

export function PublishPhase({ build, onBack }: Props) {
  const [phase, setPhase] = useState<InternalPhase>("ready");
  const [result, setResult] = useState<DoneResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [upgradeUrl, setUpgradeUrl] = useState<string | null>(null);
  const [shareLabel, setShareLabel] = useState("Copy URL");
  const [confetti, setConfetti] = useState(false);

  // If the shell ever lands here without a build (e.g. user types
  // /workspace#phase=publish into the address bar before generating
  // anything), the parent shell bootstrap snaps them back to welcome.

  async function handleInstantPublish() {
    if (!build?.slug) return;
    setPhase("publishing");
    setError(null);
    setUpgradeUrl(null);
    try {
      const r = await publishInstant(build.slug);
      setResult({ mode: "instant", data: r });
      setPhase("done");
      // Burst confetti for a beat after we render — celebrates the
      // moment without dragging on the page.
      setConfetti(true);
      setTimeout(() => setConfetti(false), 2400);
    } catch (e) {
      if (e instanceof PlanLimitError) {
        setUpgradeUrl(e.upgradeUrl);
      }
      setError(e instanceof Error ? e.message : "Publish failed.");
      setPhase("error");
    }
  }

  async function handleAdvancedPublish() {
    if (!build?.slug) return;
    setPhase("publishing");
    setError(null);
    setUpgradeUrl(null);
    try {
      const r = await publishSite(build.slug, "auto");
      setResult({ mode: "advanced", data: r });
      setPhase("done");
    } catch (e) {
      if (e instanceof PlanLimitError) {
        setUpgradeUrl(e.upgradeUrl);
      }
      setError(e instanceof Error ? e.message : "Publish failed.");
      setPhase("error");
    }
  }

  function handleShare() {
    if (!result) return;
    const url = result.mode === "instant"
      ? result.data.url
      : (result.data.url.startsWith("http") ? result.data.url : `${window.location.origin}${result.data.url}`);
    navigator.clipboard?.writeText(url);
    setShareLabel("Copied!");
    setTimeout(() => setShareLabel("Copy URL"), 1500);
  }

  const previewUrl = pickPreviewUrl(build);

  return (
    <main className="flex-1 overflow-y-auto flex flex-col items-center justify-center px-4 py-16 relative">
      {confetti && <ConfettiBurst />}
      <motion.div
        initial={{ scale: 0.4, opacity: 0, rotate: -8 }}
        animate={{ scale: 1, opacity: 1, rotate: 0 }}
        transition={{ duration: SLOW_S, ease: EASE_QUIET }}
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
        {phase === "ready" && (
          <ReadyPanel
            onInstantPublish={handleInstantPublish}
            onAdvancedPublish={handleAdvancedPublish}
            previewUrl={previewUrl}
          />
        )}
        {phase === "publishing" && <PublishingPanel />}
        {phase === "done" && result?.mode === "instant" && (
          <>
            <InstantDonePanel
              result={result.data}
              shareLabel={shareLabel}
              onShare={handleShare}
              onKeepEditing={onBack}
            />
            <DomainPanel slug={build?.slug || ""} />
          </>
        )}
        {phase === "done" && result?.mode === "advanced" && (
          <>
            <AdvancedDonePanel
              result={result.data}
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
            upgradeUrl={upgradeUrl}
            onRetry={handleInstantPublish}
            onBack={onBack}
          />
        )}
      </motion.div>
    </main>
  );
}

// ---------------------------------------------------------------------------
// Panels
// ---------------------------------------------------------------------------

function ReadyPanel({
  onInstantPublish,
  onAdvancedPublish,
  previewUrl,
}: {
  onInstantPublish: () => void;
  onAdvancedPublish: () => void;
  previewUrl: string;
}) {
  return (
    <>
      <motion.h1
        variants={{ hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0 } }}
        transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
        className={`${type.display.xl} text-foreground`}
      >
        Ready to publish?
      </motion.h1>
      <motion.div
        variants={{ hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0 } }}
        transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
        className="bg-card border border-border rounded-2xl p-8 md:p-10 shadow-[var(--shadow-1)] space-y-6"
      >
        <p className="text-muted-foreground text-base leading-relaxed">
          One click and your site is live on its own URL. Visitors can see it.
          You can share it. You can keep editing.
        </p>
        <div className="flex gap-3 justify-center flex-wrap">
          <motion.button
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.97 }}
            onClick={onInstantPublish}
            className="bg-primary text-primary-foreground px-7 py-3 rounded-full font-bold flex items-center gap-2 hover:opacity-90 shadow-[0_8px_24px_rgba(0,0,0,0.12)]"
          >
            <Rocket className="w-4 h-4" /> Publish now
          </motion.button>
          <a
            href={previewUrl}
            target="_blank"
            rel="noopener"
            className={`${interactions.chip} bg-card border border-border text-foreground px-6 py-3 rounded-full font-semibold flex items-center gap-2`}
          >
            <Eye className="w-4 h-4" /> Preview first
          </a>
        </div>
      </motion.div>

      <motion.details
        variants={{ hidden: { opacity: 0 }, visible: { opacity: 1 } }}
        className="text-left max-w-xl mx-auto"
      >
        <summary className="text-sm text-muted-foreground cursor-pointer hover:text-foreground transition-colors">
          Need a downloadable archive or custom Cloudflare deploy?
        </summary>
        <div className="mt-4 bg-card border border-border rounded-xl p-5 space-y-4">
          <p className="text-sm text-muted-foreground leading-relaxed">
            Skip the subdomain and produce a deployable ZIP instead (or push
            straight to Cloudflare Pages if your keys are configured). Useful
            when you&apos;re bringing your own host.
          </p>
          <button
            onClick={onAdvancedPublish}
            className={`${interactions.chip} bg-card border border-border text-foreground px-5 py-2 rounded-lg text-sm font-semibold flex items-center gap-2`}
          >
            <Download className="w-4 h-4" /> Advanced publish
          </button>
        </div>
      </motion.details>
    </>
  );
}

function PublishingPanel() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
      className="bg-card border border-border rounded-2xl p-12 shadow-[var(--shadow-1)] space-y-6"
    >
      {/* CSS-driven spinner (not framer) so it survives MotionConfig
          reducedMotion="user". Under reduced-motion preference, the
          rotation halts but the gap fills in (motion-reduce:border-t-primary)
          so users see a solid ring + the text below — clearly "loading,"
          not "broken UI." aria-label gives screen readers the loading
          status without depending on the visual. */}
      <div
        role="status"
        aria-label="Going live"
        className="w-12 h-12 mx-auto rounded-full border-4 border-primary border-t-transparent animate-spin motion-reduce:animate-none motion-reduce:border-t-primary"
      />
      <p className={`${type.display.m} text-foreground`}>Going live…</p>
      <p className={`${type.body.s} text-muted-foreground`}>Snapshotting + flipping the switch. Usually under a second.</p>
    </motion.div>
  );
}

function InstantDonePanel({
  result,
  shareLabel,
  onShare,
  onKeepEditing,
}: {
  result: InstantPublishResponse;
  shareLabel: string;
  onShare: () => void;
  onKeepEditing: () => void;
}) {
  const fullUrl = result.url;
  const shareText = `Just launched ${new URL(fullUrl).hostname} ✨`;

  return (
    <>
      <motion.h1
        variants={{ hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0 } }}
        transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
        className={`${type.display.xl} text-foreground`}
      >
        Your website is live.
      </motion.h1>

      <motion.div
        variants={{ hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0 } }}
        transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
        className="bg-card border border-border rounded-2xl p-8 md:p-10 shadow-[var(--shadow-1)] space-y-8"
      >
        {/* URL display — the moment of truth. Big, monospaced, copyable. */}
        <div className="flex flex-col items-center">
          <div className="bg-accent border border-border rounded-lg px-6 py-4 mb-3 flex items-center gap-3 max-w-full">
            <span className="font-mono text-lg tracking-tight text-primary truncate" title={fullUrl}>
              {fullUrl}
            </span>
          </div>
          <p className="text-muted-foreground text-xs font-bold uppercase tracking-widest">
            URL active · published in {result.elapsed_seconds?.toFixed(2) ?? "—"}s
          </p>
        </div>

        {/* Primary action row — copy, visit, edit. */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-6 border-t border-border">
          <ActionButton onClick={onShare} icon={shareLabel === "Copied!" ? Check : Share2} label={shareLabel} />
          <ActionLink href={fullUrl} icon={Eye} label="View as visitor" />
          <ActionButton onClick={onKeepEditing} icon={Edit3} label="Keep editing" />
        </div>

        {/* Social share rail — quick chips that open the native
            share-intent URL in a new tab. No SDK, no tracking, no
            third-party JS. Lucide removed brand-trademark icons so we
            label by platform name instead (also more accessible). */}
        <div className="flex flex-wrap items-center justify-center gap-2 pt-4">
          <span className="text-xs uppercase tracking-widest font-bold text-muted-foreground mr-1">
            Share on
          </span>
          <SocialChip
            href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(fullUrl)}`}
            label="X / Twitter"
          />
          <SocialChip
            href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(fullUrl)}`}
            label="LinkedIn"
          />
          <SocialChip
            href={`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(fullUrl)}`}
            label="Facebook"
          />
        </div>
      </motion.div>

      <motion.p
        variants={{ hidden: { opacity: 0 }, visible: { opacity: 1 } }}
        className="text-muted-foreground"
      >
        Everything is editable later. You don&apos;t have to be done.
      </motion.p>
    </>
  );
}

function AdvancedDonePanel({
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
        transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
        className={`${type.display.xl} text-foreground`}
      >
        {isLive ? "Your website is live." : "Your site is packaged."}
      </motion.h1>
      <motion.div
        variants={{ hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0 } }}
        transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
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

function ErrorPanel({
  error, upgradeUrl, onRetry, onBack,
}: {
  error: string;
  upgradeUrl: string | null;
  onRetry: () => void;
  onBack: () => void;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: SHORT_S, ease: EASE_CINEMATIC }}
      className="bg-card border border-destructive/40 rounded-2xl p-8 space-y-5"
    >
      <p className={`${type.display.m} text-foreground`}>
        {upgradeUrl ? "Plan limit reached." : "Publish hit a snag."}
      </p>
      <p className="text-sm text-muted-foreground break-words">{error}</p>
      <div className="flex flex-wrap gap-3 justify-center">
        {upgradeUrl ? (
          <a
            href={upgradeUrl}
            className={`${interactions.button} bg-primary text-primary-foreground px-5 py-3 rounded-full font-bold`}
          >
            Upgrade plan →
          </a>
        ) : (
          <button
            onClick={onRetry}
            className={`${interactions.button} bg-primary text-primary-foreground px-5 py-3 rounded-full font-bold`}
          >
            Try again
          </button>
        )}
        <button
          onClick={onBack}
          className={`${interactions.chip} bg-card border border-border text-foreground px-5 py-3 rounded-full font-semibold`}
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
      <span className={type.label}>{label}</span>
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
      <span className={type.label}>{label}</span>
    </motion.a>
  );
}

function SocialChip({ href, label }: { href: string; label: string }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="px-3 py-1.5 rounded-full bg-card border border-border text-xs font-semibold text-muted-foreground hover:text-primary hover:border-primary/40 transition-colors"
    >
      {label}
    </a>
  );
}

function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / 1024 / 1024).toFixed(2)} MB`;
}

// ---------------------------------------------------------------------------
// ConfettiBurst — pure-CSS confetti. ~30 paper bits in Pebble's brand
// palette, randomly placed across the top, falling with a slight sway.
// Lives inline (no extra dep) and self-cleans when the parent unmounts
// the `confetti` flag after ~2.4s. Respects prefers-reduced-motion by
// not rendering anything when the OS setting is on (the celebration
// would defeat the user's preference).
// ---------------------------------------------------------------------------

function ConfettiBurst() {
  // 30 bits is enough for "yes, this is celebratory" without being
  // visually noisy.
  const bits = Array.from({ length: 30 }, (_, i) => {
    const colors = ["#0ea5e9", "#f59e0b", "#10b981", "#ec4899", "#8b5cf6"];
    const color = colors[i % colors.length];
    const left = Math.random() * 100;
    const delay = Math.random() * 0.4;
    const duration = 1.6 + Math.random() * 1.2;
    const rotate = Math.random() * 360;
    return { color, left, delay, duration, rotate, i };
  });
  return (
    <div
      aria-hidden
      className="pointer-events-none fixed inset-0 z-50 overflow-hidden motion-reduce:hidden"
    >
      {bits.map((b) => (
        <span
          key={b.i}
          className="absolute top-0 block w-2 h-3 rounded-sm"
          style={{
            left: `${b.left}%`,
            backgroundColor: b.color,
            transform: `rotate(${b.rotate}deg)`,
            animation: `confetti-fall ${b.duration}s ${b.delay}s ease-in forwards`,
          }}
        />
      ))}
      {/* Inline keyframes — keeps the confetti self-contained, no global
          CSS needed. Tailwind doesn't have a built-in for this. */}
      <style>{`
        @keyframes confetti-fall {
          0%   { transform: translate3d(0, -20px, 0) rotate(0deg);   opacity: 1; }
          80%  { opacity: 1; }
          100% { transform: translate3d(${Math.random() > 0.5 ? "" : "-"}40px, 110vh, 0) rotate(720deg); opacity: 0; }
        }
      `}</style>
    </div>
  );
}

// ---------------------------------------------------------------------------
// DomainPanel — collapsed by default; expands into the attach/detach UI.
// Unchanged from the pre-Phase 44 version (custom-domain attachment is
// orthogonal to instant publish — it can sit on top of either).
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
      <summary className={`${type.heading.m} text-foreground cursor-pointer flex items-center gap-2`}>
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
                      ? "text-spark-deep"
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
                className={`bg-card border border-border text-muted-foreground hover:text-destructive hover:border-destructive/40 px-3 py-2 rounded-lg flex items-center gap-1 disabled:opacity-50 ${type.label}`}
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
                  className={`${interactions.chip} bg-card border border-border px-2 py-1 rounded text-xs flex items-center gap-1`}
                >
                  {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                  {copied ? "Copied" : "Copy"}
                </button>
              </div>
              <p className="text-[11px] text-muted-foreground leading-relaxed">
                After saving the record at GoDaddy / Namecheap / Cloudflare DNS / wherever, it can take
                a few minutes to propagate. We&apos;ll show <span className="text-spark-deep font-semibold">Live</span> automatically.
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
                className={`${interactions.button} bg-primary text-primary-foreground px-4 py-2 rounded-lg text-sm font-semibold disabled:opacity-40`}
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
