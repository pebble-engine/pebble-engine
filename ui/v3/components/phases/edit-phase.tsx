"use client";

import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Edit3,
  Palette,
  Smile,
  Award,
  Sparkles,
  CalendarDays,
  X,
  Undo2,
  Type as TypeIcon,
  Minus,
  Plus,
  Check,
  Monitor,
  Smartphone,
  Image as ImageIcon,
  Send,
  type LucideIcon,
} from "lucide-react";
import { BlockGallery } from "@/components/block-gallery";
import { SuggestionChips } from "@/components/workspace/suggestion-chips";
import { type PebblePlan } from "@/lib/state";
import { STANDARD_S, SHORT_S, EASE_CINEMATIC, EASE_QUIET } from "@/lib/motion";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";
import {
  insertBlock,
  isPebbleSelectMessage,
  type PebbleSelectMessage,
  refine,
  rollback,
  fetchHistory,
  visualEdit,
  chatEdit,
  pickPreviewUrl,
  fetchPreviewStatus,
  type PreviewStatus,
  type RefinementId,
  type HistorySnapshot,
  type DevServerInfo,
  type DiffSummary,
} from "@/lib/api";
import { DiffPanel } from "@/components/workspace/diff-panel";

/**
 * Design phase — the iframe preview + refine chips + visual editor +
 * version history drawer + block gallery. Used to be the whole body of
 * ``app/workspace/page.tsx``; now it's the renderer for ``phase=design``
 * in the unified workspace shell.
 *
 * Exposes an imperative handle so the shell's top-nav buttons can pop
 * the gallery / history drawer without lifting their state up. The
 * data inside the drawer (snapshot list, busy block id) stays here.
 *
 * Toasts are owned here too — every toast we emit originates from an
 * edit action that lives inside this component, so co-locating the
 * queue with the producers keeps the data flow obvious.
 */

export type EditPhaseHandle = {
  openGallery: () => void;
  openHistory: () => Promise<void>;
};

type Toast = {
  id: number;
  kind: "success" | "error";
  message: string;
  snapshotId?: string;
  slug?: string;
  /** Phase 35 — diff returned by /api/refine + /api/visual-edit. When
   *  present, the toast renders an inline compact DiffPanel below the
   *  message line so the user sees exactly what changed. */
  diff?: DiffSummary | null;
};

type Props = {
  build: {
    slug: string;
    preview_url: string;
    dev_server?: DevServerInfo | null;
  } | null;
  plan: PebblePlan | null;
  onPublish: () => void;
};

// Chip metadata — the ``billable`` flag drives the green ✨ vs amber 🪙 badge.
// "Make it friendlier", "More professional", and "Add booking" all rewrite
// text/structure via the LLM (billable). "Simpler" is a regex tone-down
// (free). "Magic Palette Shift" is a deterministic palette rotation in the
// DNA family but BILLABLE — users perceive it as a Magic Restyle and giving
// it away devalues the DNA system (NLM 2026-05-19 pricing review).
const REFINE_CHIPS: { id: RefinementId; label: string; Icon: LucideIcon; billable: boolean }[] = [
  { id: "friendlier",   label: "Make it friendlier",   Icon: Smile,        billable: true  },
  { id: "professional", label: "More professional",    Icon: Award,        billable: true  },
  { id: "simpler",      label: "Simpler",              Icon: Sparkles,     billable: false },
  { id: "colors",       label: "Magic Palette Shift",  Icon: Palette,      billable: true  },
  { id: "booking",      label: "Add booking",          Icon: CalendarDays, billable: true  },
];


export const EditPhase = forwardRef<EditPhaseHandle, Props>(function EditPhase(
  { build, plan, onPublish },
  ref,
) {
  const [iframeBust, setIframeBust] = useState(0);
  const [selected, setSelected] = useState<PebbleSelectMessage | null>(null);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [snapshots, setSnapshots] = useState<HistorySnapshot[]>([]);
  const [busyRefinement, setBusyRefinement] = useState<RefinementId | null>(null);
  const [galleryOpen, setGalleryOpen] = useState(false);
  const [busyBlockId, setBusyBlockId] = useState<string | null>(null);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [device, setDevice] = useState<"desktop" | "mobile">("desktop");
  const [chatMessage, setChatMessage] = useState("");
  const [chatBusy, setChatBusy] = useState(false);
  const [previewStatus, setPreviewStatus] = useState<PreviewStatus | null>(null);
  const toastIdRef = useRef(0);
  const previewWasReadyRef = useRef(false);

  // Poll Vercel preview deploy while the iframe may show a warmup splash.
  useEffect(() => {
    if (!build?.slug) return;
    let cancelled = false;

    async function poll() {
      try {
        const st = await fetchPreviewStatus(build.slug!);
        if (cancelled) return;
        setPreviewStatus(st);
        if (st.ready && !previewWasReadyRef.current) {
          previewWasReadyRef.current = true;
          setIframeBust((n) => n + 1);
        }
        if (!st.ready) {
          previewWasReadyRef.current = false;
        }
      } catch {
        /* owner session may lag — ignore transient poll errors */
      }
    }

    poll();
    const id = setInterval(poll, 3000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [build?.slug]);

  function pushToast(t: Omit<Toast, "id">) {
    const id = ++toastIdRef.current;
    setToasts((prev) => [...prev, { ...t, id }]);
    setTimeout(() => setToasts((prev) => prev.filter((x) => x.id !== id)), 6000);
  }

  // Listen for postMessage from the preview iframe — when the user clicks an
  // element, the bridge script sends a pebble-select event. We open the
  // right-side visual editor for that element.
  useEffect(() => {
    function onMessage(e: MessageEvent) {
      if (isPebbleSelectMessage(e.data)) {
        setSelected(e.data);
      }
    }
    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, []);

  useImperativeHandle(
    ref,
    () => ({
      openGallery: () => setGalleryOpen(true),
      openHistory: async () => {
        setHistoryOpen(true);
        if (!build?.slug) return;
        try {
          const res = await fetchHistory(build.slug);
          setSnapshots(res.snapshots);
        } catch (e) {
          pushToast({
            kind: "error",
            message: `Couldn't load history: ${e instanceof Error ? e.message : "unknown"}`,
          });
        }
      },
    }),
    [build?.slug],
  );

  async function handleRefine(refinementId: RefinementId) {
    if (!build?.slug) return;
    setBusyRefinement(refinementId);
    try {
      const result = await refine(build.slug, refinementId);
      setIframeBust((n) => n + 1);
      pushToast({
        kind: "success",
        message: result.billable
          ? `Applied "${refinementId}" (this one used credits)`
          : `Applied "${refinementId}" — free style tweak ✨`,
        snapshotId: result.snapshot_id || undefined,
        slug: build.slug,
        diff: result.diff,
      });
    } catch (e) {
      pushToast({
        kind: "error",
        message: `Refinement failed: ${e instanceof Error ? e.message : "unknown"}`,
      });
    } finally {
      setBusyRefinement(null);
    }
  }

  async function handleUndo(slug: string, snapshotId: string) {
    try {
      await rollback(slug, snapshotId);
      setIframeBust((n) => n + 1);
      pushToast({ kind: "success", message: "Rolled back. You're back to the previous version." });
    } catch (e) {
      pushToast({
        kind: "error",
        message: `Undo failed: ${e instanceof Error ? e.message : "unknown"}`,
      });
    }
  }

  async function handleRollbackTo(snapshotId: string) {
    if (!build?.slug) return;
    try {
      await rollback(build.slug, snapshotId);
      setIframeBust((n) => n + 1);
      pushToast({ kind: "success", message: "Restored. Your site is back to that version." });
      const res = await fetchHistory(build.slug);
      setSnapshots(res.snapshots);
    } catch (e) {
      pushToast({
        kind: "error",
        message: `Restore failed: ${e instanceof Error ? e.message : "unknown"}`,
      });
    }
  }

  // Visual edit handlers — these all call /api/visual-edit and report
  // billable:false so the user never sees an unexpected charge.
  async function handleTextEdit(newText: string) {
    if (!selected || !build?.slug) return;
    if (newText === selected.text) {
      setSelected(null);
      return;
    }
    try {
      const result = await visualEdit({
        slug: build.slug,
        op: "text",
        pebble_id: selected.pebble_id || undefined,
        original_text: selected.text,
        new_text: newText,
      });
      // Don't claim success on a no-op (text not found anywhere). Previously
      // every 200 read as "Text updated" even when nothing changed.
      if (result.no_match || !result.files_changed?.length) {
        pushToast({
          kind: "error",
          message: "Couldn't find that text to edit — try selecting it again.",
        });
        setSelected(null);
        return;
      }
      setIframeBust((n) => n + 1);
      pushToast({
        kind: "success",
        message: result.used_manifest
          ? "Text updated (surgical). Free tweak ✨"
          : result.ambiguous
            ? "Updated — but multiple files matched, double-check."
            : "Text updated. Free tweak ✨",
        snapshotId: result.snapshot_id || undefined,
        slug: build.slug,
        diff: result.diff,
      });
      setSelected(null);
    } catch (e) {
      pushToast({
        kind: "error",
        message: `Edit failed: ${e instanceof Error ? e.message : "unknown"}`,
      });
    }
  }

  async function handleFontSizeStep(delta: number) {
    if (!selected || !build?.slug) return;
    // With a pebble_id, compute target px so the surgical path can drop an
    // inline style. Without one, the engine falls back to Tailwind text-*
    // step rotation using delta alone.
    let newFontSize: string | undefined;
    if (selected.pebble_id && selected.style?.fontSize) {
      const cur = parseFloat(selected.style.fontSize);
      if (!Number.isNaN(cur) && cur > 0) {
        const target = Math.max(10, Math.round(cur + delta * 2));
        newFontSize = `${target}px`;
      }
    }
    try {
      const result = await visualEdit({
        slug: build.slug,
        op: "font-size",
        pebble_id: selected.pebble_id || undefined,
        selector_hint: selected.text || selected.className,
        new_font_size: newFontSize,
        delta,
      });
      setIframeBust((n) => n + 1);
      pushToast({
        kind: "success",
        message: `Font size ${delta > 0 ? "increased" : "decreased"}. Free tweak ✨`,
        snapshotId: result.snapshot_id || undefined,
        slug: build.slug,
        diff: result.diff,
      });
    } catch (e) {
      pushToast({
        kind: "error",
        message: `Font edit failed: ${e instanceof Error ? e.message : "unknown"}`,
      });
    }
  }

  async function handleInsertBlock(blockId: string) {
    if (!build?.slug || busyBlockId) return;
    setBusyBlockId(blockId);
    try {
      const result = await insertBlock(build.slug, blockId);
      setIframeBust((n) => n + 1);
      setGalleryOpen(false);
      pushToast({
        kind: "success",
        message: `Added "${result.component_name}" — themed against ${result.dna_label || "your site"}. Free ✨`,
        snapshotId: result.snapshot_id || undefined,
        slug: build.slug,
        diff: result.diff,
      });
    } catch (e) {
      pushToast({
        kind: "error",
        message: `Add failed: ${e instanceof Error ? e.message : "unknown"}`,
      });
    } finally {
      setBusyBlockId(null);
    }
  }

  async function handleColor(hex: string) {
    if (!selected || !build?.slug) return;
    try {
      const result = await visualEdit({
        slug: build.slug,
        op: "color",
        pebble_id: selected.pebble_id || undefined,
        selector_hint: selected.text || selected.className,
        new_color: hex,
      });
      setIframeBust((n) => n + 1);
      pushToast({
        kind: "success",
        message: "Color updated. Free tweak ✨",
        snapshotId: result.snapshot_id || undefined,
        slug: build.slug,
        diff: result.diff,
      });
    } catch (e) {
      pushToast({
        kind: "error",
        message: `Color edit failed: ${e instanceof Error ? e.message : "unknown"}`,
      });
    }
  }

  async function handleFontFamily(fontName: string) {
    if (!selected || !build?.slug) return;
    try {
      const result = await visualEdit({
        slug: build.slug,
        op: "font-family",
        pebble_id: selected.pebble_id || undefined,
        selector_hint: selected.text || selected.className,
        new_font_family: fontName,
      });
      setIframeBust((n) => n + 1);
      pushToast({
        kind: "success",
        message: `Font changed to ${fontName}. Free tweak ✨`,
        snapshotId: result.snapshot_id || undefined,
        slug: build.slug,
        diff: result.diff,
      });
    } catch (e) {
      pushToast({
        kind: "error",
        message: `Font edit failed: ${e instanceof Error ? e.message : "unknown"}`,
      });
    }
  }

  async function handleImageSwap(newSrc: string) {
    if (!selected || !build?.slug) return;
    try {
      const result = await visualEdit({
        slug: build.slug,
        op: "image-swap",
        pebble_id: selected.pebble_id || undefined,
        selector_hint: selected.className,
        original_src: selected.src ?? "",
        new_src: newSrc,
      });
      setIframeBust((n) => n + 1);
      pushToast({
        kind: "success",
        message: "Image swapped. Free tweak ✨",
        snapshotId: result.snapshot_id || undefined,
        slug: build.slug,
        diff: result.diff,
      });
      setSelected(null);
    } catch (e) {
      pushToast({
        kind: "error",
        message: `Image swap failed: ${e instanceof Error ? e.message : "unknown"}`,
      });
    }
  }

  async function handleChatEdit() {
    if (!build?.slug || !chatMessage.trim() || chatBusy) return;
    const msg = chatMessage.trim();
    setChatMessage("");
    setChatBusy(true);
    try {
      const result = await chatEdit(build.slug, msg);
      if (result.matched) {
        setIframeBust((n) => n + 1);
        pushToast({
          kind: "success",
          message: result.billable
            ? `Applied: "${msg}" (used credits)`
            : `Applied: "${msg}" — free tweak ✨`,
          snapshotId: result.snapshot_id || undefined,
          slug: build.slug,
          diff: result.diff,
        });
      } else {
        pushToast({
          kind: "error",
          message: `Couldn't apply that yet — try: "${result.suggestion}"`,
        });
      }
    } catch (e) {
      pushToast({
        kind: "error",
        message: `Chat edit failed: ${e instanceof Error ? e.message : "unknown"}`,
      });
    } finally {
      setChatBusy(false);
    }
  }

  const basePreview = pickPreviewUrl(build);
  const previewUrl = basePreview === "about:blank"
    ? "about:blank"
    : `${basePreview}${basePreview.includes("?") ? "&" : "?"}v=${iframeBust}`;
  const slugForUrl = build?.slug || "your-site";

  return (
    <>
      {/* Center — full-bleed site preview iframe. No outer padding so the
          iframe fills edge-to-edge. The chrome strip (URL bar + device
          toggle) sits flush at the top of the preview area. */}
      <main className="flex-1 bg-background relative overflow-hidden flex flex-col">
        {/* Chrome strip — URL pill + device toggle. Flush to the top of
            the preview area (no outer padding on <main>). */}
        <motion.div
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
          className="h-10 bg-accent flex items-center px-4 gap-2 border-b border-border shrink-0"
        >
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-border" />
            <div className="w-3 h-3 rounded-full bg-border opacity-60" />
            <div className="w-3 h-3 rounded-full bg-border opacity-30" />
          </div>
          <div className="bg-background border border-border px-4 py-0.5 rounded-full text-xs text-muted-foreground mx-auto truncate max-w-[50%]">
            {slugForUrl}.pebbleapp.ai
          </div>
          {/* Desktop / mobile device toggle. Mobile constrains the iframe
              wrapper to ~390px so the user can verify the responsive
              layout without resizing their actual browser window. */}
          <div className="flex items-center gap-0.5 bg-background border border-border rounded-full p-0.5">
            <button
              onClick={() => setDevice("desktop")}
              aria-label="Desktop preview"
              aria-pressed={device === "desktop"}
              className={`${interactions.focusRing} transition-colors duration-150 ease-out w-7 h-7 rounded-full flex items-center justify-center active:scale-95 motion-reduce:active:scale-100 ${
                device === "desktop"
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground"
              }`}
            >
              <Monitor className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setDevice("mobile")}
              aria-label="Mobile preview"
              aria-pressed={device === "mobile"}
              className={`${interactions.focusRing} transition-colors duration-150 ease-out w-7 h-7 rounded-full flex items-center justify-center active:scale-95 motion-reduce:active:scale-100 ${
                device === "mobile"
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground"
              }`}
            >
              <Smartphone className="w-3.5 h-3.5" />
            </button>
          </div>
        </motion.div>

        {/* Full-bleed iframe — fills the remaining space below the chrome strip */}
        <div className={`flex-1 bg-background flex justify-center overflow-hidden relative ${device === "mobile" ? "p-4 overflow-y-auto" : ""}`}>
          {previewStatus && !previewStatus.ready && (
            <div className="absolute inset-0 z-20 flex items-center justify-center bg-background/80 backdrop-blur-sm px-6">
              <div className="max-w-md text-center space-y-2">
                <p className={`${type.body.m} text-foreground font-medium`}>
                  {previewStatus.deploying
                    ? "Building your preview…"
                    : previewStatus.error
                      ? "Preview needs another try"
                      : "Starting preview…"}
                </p>
                <p className={`${type.body.s} text-muted-foreground`}>
                  {previewStatus.deploying
                    ? "First compile on Vercel usually takes 1–2 minutes."
                    : previewStatus.error
                      ? previewStatus.error
                      : previewStatus.has_source
                        ? "Hang tight — we're preparing your site."
                        : "Project files missing on the server — try rebuilding."}
                </p>
              </div>
            </div>
          )}
          <iframe
            src={previewUrl}
            className={`bg-white transition-[max-width] duration-300 ease-out ${
              device === "mobile"
                ? "w-full max-w-[390px] rounded-2xl border border-border shadow-[var(--shadow-1)]"
                : "w-full max-w-none"
            }`}
            style={{ height: "100%" }}
            title="Site preview"
          />
        </div>

        {/* 2026-05-23: Bottom chips dock REMOVED per Marc's design directive.
            The "STYLE TWEAKS ARE FREE" eyebrow, refinement chips (Make it
            friendlier / More professional / Simpler / Magic Palette Shift /
            Add booking), SuggestionChips (Add testimonials / pricing / etc),
            and "Ask a change…" chat bar all lived here. They cluttered the
            preview surface. Edits now come from:
              1. Click any element in the preview → VisualEditorPanel slides
                 in from the right (font / color / font-size)
              2. The icons next to the URL bar at the top of the preview
                 (desktop / mobile / publish-status toggle)
              3. "+ Add section" button in the TopNav (block insertion)
            handleRefine / handleChatEdit / handleInsertBlock callbacks are
            kept for future re-wiring if a different surface needs them. */}
      </main>

      {/* Visual Editor overlay — slides in from the right edge of the preview
          area when the user clicks an element in the iframe. Absolute-
          positioned over the preview (not a flex sibling) so it doesn't
          consume layout space. Backdrop gives it a layered feel. */}
      <AnimatePresence>
        {selected && (
          <>
            {/* Semi-transparent backdrop — clicking it closes the panel */}
            <motion.div
              key="editor-backdrop"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: SHORT_S, ease: EASE_CINEMATIC }}
              onClick={() => setSelected(null)}
              className="fixed inset-0 bg-charcoal/20 z-30 pointer-events-auto"
              style={{ left: 'var(--left-rail-w, 240px)' }}
            />
            <VisualEditorPanel
              key="editor"
              selected={selected}
              onClose={() => setSelected(null)}
              onText={handleTextEdit}
              onFontSize={handleFontSizeStep}
              onColor={handleColor}
              onFontFamily={handleFontFamily}
              onImageSwap={handleImageSwap}
            />
          </>
        )}
      </AnimatePresence>

      {/* Version history drawer */}
      <AnimatePresence>
        {historyOpen && (
          <HistoryDrawer
            snapshots={snapshots}
            onClose={() => setHistoryOpen(false)}
            onRollback={(id) => {
              setHistoryOpen(false);
              handleRollbackTo(id);
            }}
          />
        )}
      </AnimatePresence>

      {/* Block library modal — DNA-themed drop-in sections */}
      <BlockGallery
        open={galleryOpen}
        busyBlockId={busyBlockId}
        onClose={() => setGalleryOpen(false)}
        onInsert={handleInsertBlock}
      />

      {/* Toast stack */}
      <div className="fixed top-20 right-6 z-[60] flex flex-col gap-2 pointer-events-none">
        <AnimatePresence>
          {toasts.map((t) => (
            <motion.div
              key={t.id}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: SHORT_S, ease: EASE_CINEMATIC }}
              className={`pointer-events-auto rounded-xl border shadow-lg px-4 py-3 max-w-sm ${
                t.kind === "success"
                  ? "bg-card border-border border-l-4 border-l-green-500 text-foreground"
                  : "bg-destructive/10 border-destructive/40 text-destructive"
              }`}
            >
              <div className="flex items-start gap-3">
                {t.kind === "success" && (
                  <Check className="w-4 h-4 text-green-500 shrink-0 mt-0.5" />
                )}
                <div className="flex-1 text-sm">{t.message}</div>
                {t.snapshotId && t.slug && (
                  <button
                    onClick={() => handleUndo(t.slug!, t.snapshotId!)}
                    className={`${interactions.link} text-xs font-bold text-primary flex items-center gap-1`}
                  >
                    <Undo2 className="w-3 h-3" /> Undo
                  </button>
                )}
              </div>
              {/* Phase 35 — show the diff inline when we have one. Compact
                  mode keeps the toast small; users see exactly what touched
                  ("Updated 3 files across Frontend, Config") without
                  scrolling or opening another panel. */}
              {t.kind === "success" && t.diff && t.diff.total_changed > 0 && (
                <div className="mt-2 pl-7">
                  <DiffPanel diff={t.diff} mode="compact" />
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </>
  );
});

// ---------------------------------------------------------------------------
// VisualEditorPanel — absolute overlay when an element on the preview is selected
// ---------------------------------------------------------------------------

function VisualEditorPanel({
  selected,
  onClose,
  onText,
  onFontSize,
  onColor,
  onFontFamily,
  onImageSwap,
}: {
  selected: PebbleSelectMessage;
  onClose: () => void;
  onText: (newText: string) => void;
  onFontSize: (delta: number) => void;
  onColor: (hex: string) => void;
  onFontFamily: (fontName: string) => void;
  onImageSwap: (newSrc: string) => void;
}) {
  const [textDraft, setTextDraft] = useState(selected.text);
  const [imageSrcDraft, setImageSrcDraft] = useState(selected.src ?? "");
  useEffect(() => {
    setTextDraft(selected.text);
    setImageSrcDraft(selected.src ?? "");
  }, [selected]);

  const PALETTE = [
    "#1F1D1A", "#205661", "#4B6548", "#C76E3A", "#5A554E",
    "#F7F3EC", "#ECE6DC", "#D8D1C5", "#EFEAE1", "#FFFFFF",
  ];

  const FONT_FAMILIES = [
    "Inter",
    "Playfair Display",
    "DM Sans",
    "Lato",
    "Space Grotesk",
    "Merriweather",
    "JetBrains Mono",
  ];

  const isImage = selected.tag === "img";

  return (
    <motion.aside
      initial={{ opacity: 0, x: 16 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 16 }}
      transition={{ duration: SHORT_S, ease: EASE_CINEMATIC }}
      className="fixed top-16 bottom-0 right-0 w-[360px] flex flex-col gap-4 p-5 bg-card border-l border-border overflow-y-auto z-40 shadow-[var(--shadow-2)]"
    >
      <div className="flex justify-between items-start">
        <div>
          <p className="text-[11px] font-mono uppercase tracking-widest text-earth-deep">Free style tweak ✨</p>
          <h2 className={`${type.heading.m} text-primary mt-1`}>
            Editing {selected.tag.toUpperCase()}
          </h2>
        </div>
        <button
          onClick={onClose}
          className={`${interactions.iconButton} w-8 h-8 rounded-full flex items-center justify-center`}
          aria-label="Close editor"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Phase 56c — image swap: when an <img> is selected show URL swap controls
          instead of text / font / color (those don't apply to images). */}
      {isImage ? (
        <div className="space-y-2">
          <label className={`${type.eyebrow} flex items-center gap-1`}>
            <ImageIcon className="w-3 h-3" /> Swap image
          </label>
          {selected.src && (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={selected.src}
              alt="Current image"
              className="w-full h-24 object-cover rounded-lg border border-border"
            />
          )}
          <input
            type="url"
            value={imageSrcDraft}
            onChange={(e) => setImageSrcDraft(e.target.value)}
            placeholder="https://images.unsplash.com/…"
            className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
          <button
            onClick={() => onImageSwap(imageSrcDraft)}
            disabled={!imageSrcDraft.trim() || imageSrcDraft === selected.src}
            className={`${interactions.button} w-full bg-primary text-primary-foreground py-2 rounded-lg text-sm font-semibold disabled:opacity-40 flex items-center justify-center gap-2`}
          >
            <Check className="w-4 h-4" /> Swap image
          </button>
          <p className="text-xs text-muted-foreground italic">
            Paste any public image URL — Unsplash, Pexels, or your own CDN.
          </p>
        </div>
      ) : (
        <>
          {/* Text editor — only show when the element actually has text content */}
          {selected.text && selected.text.trim() && (
            <div className="space-y-2">
              <label className={`${type.eyebrow} flex items-center gap-1`}>
                <Edit3 className="w-3 h-3" /> Text
              </label>
              <textarea
                value={textDraft}
                onChange={(e) => setTextDraft(e.target.value)}
                rows={Math.min(6, Math.max(2, Math.ceil(textDraft.length / 40)))}
                className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-none"
              />
              <button
                onClick={() => onText(textDraft)}
                disabled={textDraft === selected.text}
                className={`${interactions.button} w-full bg-primary text-primary-foreground py-2 rounded-lg text-sm font-semibold disabled:opacity-40 flex items-center justify-center gap-2`}
              >
                <Check className="w-4 h-4" /> Save text
              </button>
            </div>
          )}

          {/* Font size stepper */}
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground flex items-center gap-1">
              <TypeIcon className="w-3 h-3" /> Font size
            </label>
            <div className="flex items-center gap-2">
              <button
                onClick={() => onFontSize(-1)}
                className={`${interactions.chip} flex-1 bg-background border border-border rounded-lg py-2 flex items-center justify-center gap-1 text-sm font-semibold`}
              >
                <Minus className="w-4 h-4" /> Smaller
              </button>
              <button
                onClick={() => onFontSize(1)}
                className={`${interactions.chip} flex-1 bg-background border border-border rounded-lg py-2 flex items-center justify-center gap-1 text-sm font-semibold`}
              >
                <Plus className="w-4 h-4" /> Larger
              </button>
            </div>
            <p className="text-xs text-muted-foreground italic">Currently {selected.style.fontSize}</p>
          </div>

          {/* Phase 56b — font family picker (curated list of Google-safe families) */}
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground flex items-center gap-1">
              <TypeIcon className="w-3 h-3" /> Font family
            </label>
            <div className="flex flex-wrap gap-1.5">
              {FONT_FAMILIES.map((font) => (
                <button
                  key={font}
                  onClick={() => onFontFamily(font)}
                  className={`${interactions.chip} px-2.5 py-1 text-xs rounded-full border border-border hover:border-primary hover:bg-accent transition-colors`}
                  style={{ fontFamily: font }}
                >
                  {font}
                </button>
              ))}
            </div>
          </div>

          {/* Color picker — Pebble palette + free hex input */}
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground flex items-center gap-1">
              <Palette className="w-3 h-3" /> Color
            </label>
            <div className="grid grid-cols-5 gap-2">
              {PALETTE.map((hex) => (
                <button
                  key={hex}
                  onClick={() => onColor(hex)}
                  className="aspect-square rounded-lg border-2 border-border hover:border-primary transition-colors"
                  style={{ backgroundColor: hex }}
                  title={hex}
                  aria-label={`Set color to ${hex}`}
                />
              ))}
            </div>
            {/* Phase 56b — native color picker for any hex the user wants */}
            <div className="flex items-center gap-2 pt-1">
              <input
                type="color"
                defaultValue="#205661"
                onChange={(e) => onColor(e.target.value)}
                className="w-8 h-8 rounded border border-border cursor-pointer bg-transparent p-0.5"
                title="Custom color"
                aria-label="Pick custom color"
              />
              <span className="text-xs text-muted-foreground">Custom color</span>
            </div>
          </div>
        </>
      )}

      <div className="mt-auto pt-4 border-t border-border">
        <p className="text-[11px] text-muted-foreground italic leading-snug">
          Click anywhere on the preview to pick another element. Every change you make here is free and undoable.
        </p>
      </div>
    </motion.aside>
  );
}

// ---------------------------------------------------------------------------
// HistoryDrawer — full-height right drawer over the whole workspace
// ---------------------------------------------------------------------------

function HistoryDrawer({
  snapshots,
  onClose,
  onRollback,
}: {
  snapshots: HistorySnapshot[];
  onClose: () => void;
  onRollback: (snapshotId: string) => void;
}) {
  return (
    <>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: SHORT_S, ease: EASE_CINEMATIC }}
        onClick={onClose}
        className="fixed inset-0 bg-charcoal/30 backdrop-blur-sm z-40"
      />
      <motion.aside
        initial={{ x: "100%" }}
        animate={{ x: 0 }}
        exit={{ x: "100%" }}
        transition={{ duration: STANDARD_S, ease: EASE_QUIET }}
        className="fixed top-0 right-0 bottom-0 w-[440px] bg-card border-l border-border z-50 flex flex-col"
      >
        <div className="p-5 border-b border-border flex justify-between items-start">
          <div>
            <h2 className={`${type.heading.l} text-primary`}>Version history</h2>
            <p className="text-xs text-muted-foreground mt-1">
              Every change creates a snapshot. Roll back any time.
            </p>
          </div>
          <button
            onClick={onClose}
            className={`${interactions.iconButton} w-9 h-9 rounded-full flex items-center justify-center`}
            aria-label="Close history"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {snapshots.length === 0 && (
            <p className="text-sm text-muted-foreground text-center py-10">
              No snapshots yet. The first one will appear after your next change.
            </p>
          )}
          {snapshots.map((s, i) => (
            <motion.div
              key={s.snapshot_id}
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.04 * i, duration: SHORT_S, ease: EASE_CINEMATIC }}
              className="p-4 rounded-xl bg-background border border-border hover:border-primary/50 transition-colors"
            >
              <div className="flex justify-between items-start gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <ReasonBadge reason={s.reason} />
                    {/* Humanized relative time — easier to scan than an
                        ISO date. Hover the row for the raw snapshot_id
                        (power-user affordance via the wrapper `title`). */}
                    <span
                      className="text-xs text-muted-foreground"
                      title={`${formatTimestamp(s.written_at)} · ${s.snapshot_id}`}
                    >
                      {formatRelativeTime(s.written_at)}
                      {typeof s.files_count === "number" && s.files_count > 0
                        ? ` · ${s.files_count} ${s.files_count === 1 ? "file" : "files"} changed`
                        : ""}
                    </span>
                  </div>
                  <p className="text-sm text-foreground truncate">{s.source || s.reason}</p>
                </div>
                <button
                  onClick={() => onRollback(s.snapshot_id)}
                  className={`${interactions.chip} flex items-center gap-1 bg-card border border-border text-foreground px-3 py-2 rounded-lg shrink-0 ${type.label}`}
                >
                  <Undo2 className="w-3 h-3" /> Restore
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.aside>
    </>
  );
}

function ReasonBadge({ reason }: { reason: string }) {
  const style = reason.startsWith("refine")
    ? { bg: "bg-secondary/20", text: "text-secondary", label: reason.replace("refine-", "") }
    : reason.startsWith("visual-edit")
      ? { bg: "bg-earth/20",      text: "text-earth-deep", label: reason.replace("visual-edit-", "") }
      : reason === "generate"
        ? { bg: "bg-primary/15",  text: "text-primary",    label: "Generated" }
        : reason === "restore"
          ? { bg: "bg-spark/15",  text: "text-spark-deep", label: "Restored" }
          : { bg: "bg-muted",     text: "text-muted-foreground", label: reason };
  return (
    <span className={`text-[11px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${style.bg} ${style.text}`}>
      {style.label}
    </span>
  );
}

function formatTimestamp(iso: string): string {
  if (!iso) return "";
  try {
    const d = new Date(iso);
    return d.toLocaleString([], { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
  } catch {
    return iso;
  }
}

// Humanizes an ISO timestamp into "5 minutes ago", "2 hours ago", "yesterday",
// etc. via Intl.RelativeTimeFormat — picks the largest unit that fits so the
// label stays scannable. Falls back to formatTimestamp on parse failure.
function formatRelativeTime(iso: string): string {
  if (!iso) return "";
  try {
    const t = new Date(iso).getTime();
    if (Number.isNaN(t)) return formatTimestamp(iso);
    const diffSec = Math.round((t - Date.now()) / 1000); // negative for the past
    const rtf = new Intl.RelativeTimeFormat(undefined, { numeric: "auto" });
    const abs = Math.abs(diffSec);
    if (abs < 45)         return rtf.format(Math.round(diffSec), "second");
    if (abs < 60 * 45)    return rtf.format(Math.round(diffSec / 60), "minute");
    if (abs < 3600 * 22)  return rtf.format(Math.round(diffSec / 3600), "hour");
    if (abs < 86400 * 6)  return rtf.format(Math.round(diffSec / 86400), "day");
    if (abs < 86400 * 27) return rtf.format(Math.round(diffSec / (86400 * 7)), "week");
    if (abs < 86400 * 320) return rtf.format(Math.round(diffSec / (86400 * 30)), "month");
    return rtf.format(Math.round(diffSec / (86400 * 365)), "year");
  } catch {
    return formatTimestamp(iso);
  }
}
