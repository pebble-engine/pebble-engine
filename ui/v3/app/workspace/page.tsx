"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Lightbulb,
  Map,
  Edit3,
  Palette,
  Puzzle,
  Settings,
  Rocket,
  Smile,
  Award,
  Sparkles,
  CalendarDays,
  History,
  X,
  Undo2,
  Coins,
  Type as TypeIcon,
  Minus,
  Plus,
  Check,
  type LucideIcon,
} from "lucide-react";
import { TopNav } from "@/components/top-nav";
import { getBrief, getLastBuild, getPlan, type PebblePlan } from "@/lib/state";
import {
  isPebbleSelectMessage,
  type PebbleSelectMessage,
  refine,
  rollback,
  fetchHistory,
  visualEdit,
  type RefinementId,
  type HistorySnapshot,
} from "@/lib/api";

type Step = { id: string; label: string; Icon: LucideIcon };

const BUILD_PLAN: Step[] = [
  { id: "idea",     label: "Idea",     Icon: Lightbulb },
  { id: "plan",     label: "Plan",     Icon: Map },
  { id: "draft",    label: "Draft",    Icon: Edit3 },
  { id: "design",   label: "Design",   Icon: Palette },
  { id: "features", label: "Features", Icon: Puzzle },
  { id: "setup",    label: "Setup",    Icon: Settings },
  { id: "publish",  label: "Publish",  Icon: Rocket },
];

// Chip metadata — the `billable` flag drives the green ✨ vs amber 🪙 badge.
// "Make it friendlier", "More professional", and "Add booking" all rewrite
// text/structure via the LLM (billable). "Simpler" and "Change colors" are
// pure regex swaps in CSS/Tailwind config (free).
const REFINE_CHIPS: { id: RefinementId; label: string; Icon: LucideIcon; billable: boolean }[] = [
  { id: "friendlier",   label: "Make it friendlier",  Icon: Smile,        billable: true  },
  { id: "professional", label: "More professional",   Icon: Award,        billable: true  },
  { id: "simpler",      label: "Simpler",             Icon: Sparkles,     billable: false },
  { id: "colors",       label: "Change colors",       Icon: Palette,      billable: false },
  { id: "booking",      label: "Add booking",         Icon: CalendarDays, billable: true  },
];

type Toast = {
  id: number;
  kind: "success" | "error";
  message: string;
  snapshotId?: string;  // present when an action is undoable
  slug?: string;
};

export default function WorkspacePage() {
  const router = useRouter();
  const [plan, setPlan] = useState<PebblePlan | null>(null);
  const [build, setBuild] = useState<ReturnType<typeof getLastBuild>>(null);
  const [brief, setBrief] = useState<ReturnType<typeof getBrief>>({});
  const [iframeBust, setIframeBust] = useState(0);          // increments to force iframe reload
  const [selected, setSelected] = useState<PebbleSelectMessage | null>(null);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [snapshots, setSnapshots] = useState<HistorySnapshot[]>([]);
  const [busyRefinement, setBusyRefinement] = useState<RefinementId | null>(null);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const toastIdRef = useRef(0);

  useEffect(() => {
    setPlan(getPlan());
    setBuild(getLastBuild());
    setBrief(getBrief());
    if (!getLastBuild()) router.push("/");
  }, [router]);

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

  function pushToast(t: Omit<Toast, "id">) {
    const id = ++toastIdRef.current;
    setToasts((prev) => [...prev, { ...t, id }]);
    // Auto-dismiss after 6s (give time to hit Undo)
    setTimeout(() => setToasts((prev) => prev.filter((x) => x.id !== id)), 6000);
  }

  async function handleRefine(refinementId: RefinementId) {
    if (!build?.slug) return;
    setBusyRefinement(refinementId);
    try {
      const result = await refine(build.slug as string, refinementId);
      setIframeBust((n) => n + 1);
      pushToast({
        kind: "success",
        message: result.billable
          ? `Applied "${refinementId}" (this one used credits)`
          : `Applied "${refinementId}" — free style tweak ✨`,
        snapshotId: result.snapshot_id || undefined,
        slug: build.slug as string,
      });
    } catch (e) {
      pushToast({ kind: "error", message: `Refinement failed: ${e instanceof Error ? e.message : "unknown"}` });
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
      pushToast({ kind: "error", message: `Undo failed: ${e instanceof Error ? e.message : "unknown"}` });
    }
  }

  async function openHistory() {
    if (!build?.slug) return;
    setHistoryOpen(true);
    try {
      const res = await fetchHistory(build.slug as string);
      setSnapshots(res.snapshots);
    } catch (e) {
      pushToast({ kind: "error", message: `Couldn't load history: ${e instanceof Error ? e.message : "unknown"}` });
    }
  }

  async function handleRollbackTo(snapshotId: string) {
    if (!build?.slug) return;
    try {
      await rollback(build.slug as string, snapshotId);
      setIframeBust((n) => n + 1);
      pushToast({ kind: "success", message: "Restored. Your site is back to that version." });
      const res = await fetchHistory(build.slug as string);
      setSnapshots(res.snapshots);
    } catch (e) {
      pushToast({ kind: "error", message: `Restore failed: ${e instanceof Error ? e.message : "unknown"}` });
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
        slug: build.slug as string,
        op: "text",
        original_text: selected.text,
        new_text: newText,
      });
      setIframeBust((n) => n + 1);
      pushToast({
        kind: "success",
        message: result.ambiguous ? "Updated — but multiple files matched, double-check." : "Text updated. Free tweak ✨",
        snapshotId: result.snapshot_id || undefined,
        slug: build.slug as string,
      });
      setSelected(null);
    } catch (e) {
      pushToast({ kind: "error", message: `Edit failed: ${e instanceof Error ? e.message : "unknown"}` });
    }
  }

  async function handleFontSizeStep(delta: number) {
    if (!selected || !build?.slug) return;
    try {
      const result = await visualEdit({
        slug: build.slug as string,
        op: "font-size",
        selector_hint: selected.text || selected.className,
        delta,
      });
      setIframeBust((n) => n + 1);
      pushToast({
        kind: "success",
        message: `Font size ${delta > 0 ? "increased" : "decreased"}. Free tweak ✨`,
        snapshotId: result.snapshot_id || undefined,
        slug: build.slug as string,
      });
    } catch (e) {
      pushToast({ kind: "error", message: `Font edit failed: ${e instanceof Error ? e.message : "unknown"}` });
    }
  }

  async function handleColor(hex: string) {
    if (!selected || !build?.slug) return;
    try {
      const result = await visualEdit({
        slug: build.slug as string,
        op: "color",
        selector_hint: selected.text || selected.className,
        new_color: hex,
      });
      setIframeBust((n) => n + 1);
      pushToast({
        kind: "success",
        message: "Color updated. Free tweak ✨",
        snapshotId: result.snapshot_id || undefined,
        slug: build.slug as string,
      });
    } catch (e) {
      pushToast({ kind: "error", message: `Color edit failed: ${e instanceof Error ? e.message : "unknown"}` });
    }
  }

  const projectName = (brief.business_name as string) || "Untitled Project";
  const previewUrl = build?.preview_url ? `${build.preview_url}?v=${iframeBust}` : "about:blank";
  const slugForUrl = (build?.slug as string) || "your-site";

  return (
    <div className="min-h-screen flex flex-col">
      <TopNav
        projectName={projectName}
        rightSlot={
          <button
            onClick={openHistory}
            title="Version history"
            className="w-10 h-10 rounded-full flex items-center justify-center text-graphite hover:bg-mist hover:text-charcoal dark:text-pebble dark:hover:bg-stone/40 dark:hover:text-sand transition-colors"
            aria-label="Open version history"
          >
            <History className="w-5 h-5" />
          </button>
        }
      />

      <div className="flex flex-1 overflow-hidden">
        {/* Left rail — Build Plan */}
        <motion.aside
          initial={{ opacity: 0, x: -8 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4 }}
          className="flex flex-col gap-1 p-4 w-[240px] bg-card border-r border-border"
        >
          <div className="mb-6 px-1">
            <h2 className="font-display text-xl font-semibold text-primary leading-tight">Your Build Plan</h2>
            <p className="text-xs text-muted-foreground opacity-70">AI-Guided Strategy</p>
          </div>
          <nav className="flex flex-col gap-1">
            {BUILD_PLAN.map((s, i) => (
              <motion.button
                key={s.id}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.06 * i, duration: 0.3 }}
                className={`flex items-center gap-2 p-2.5 rounded-lg text-sm font-semibold transition-colors ${
                  s.id === "draft"
                    ? "bg-primary/15 text-primary"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground"
                }`}
              >
                <s.Icon className="w-5 h-5 shrink-0" />
                <span>{s.label}</span>
              </motion.button>
            ))}
          </nav>
        </motion.aside>

        {/* Center — site preview iframe */}
        <main className="flex-1 bg-background p-6 relative overflow-hidden flex flex-col">
          <motion.div
            initial={{ opacity: 0, scale: 0.99 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4 }}
            className="flex-1 rounded-2xl border border-border bg-card shadow-[var(--shadow-1)] overflow-hidden flex flex-col"
          >
            <div className="h-10 bg-accent flex items-center px-4 gap-2 border-b border-border">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-border" />
                <div className="w-3 h-3 rounded-full bg-border opacity-60" />
                <div className="w-3 h-3 rounded-full bg-border opacity-30" />
              </div>
              <div className="bg-background border border-border px-4 py-0.5 rounded-full text-xs text-muted-foreground mx-auto truncate max-w-[60%]">
                {slugForUrl}.pebble.site
              </div>
            </div>
            <iframe
              src={previewUrl}
              className="flex-1 bg-white w-full"
              title="Site preview"
            />
          </motion.div>

          {/* Refinement chips bar */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, delay: 0.15 }}
            className="fixed bottom-6 left-[240px] right-[320px] flex flex-col items-center gap-2 pointer-events-none"
          >
            <p className="text-[11px] font-mono uppercase tracking-widest text-muted-foreground bg-card/80 backdrop-blur px-3 py-1 rounded-full border border-border pointer-events-auto">
              ✨ Style tweaks are free — click an element on the preview or pick a chip below
            </p>
            <nav className="bg-card border border-border shadow-lg rounded-full px-3 py-2 flex gap-1 pointer-events-auto">
              {REFINE_CHIPS.map((c) => {
                const isBusy = busyRefinement === c.id;
                return (
                  <motion.button
                    key={c.id}
                    whileHover={{ y: -3 }}
                    whileTap={{ scale: 0.95 }}
                    disabled={isBusy || busyRefinement !== null}
                    onClick={() => handleRefine(c.id)}
                    className="relative text-muted-foreground px-4 py-1.5 text-sm font-semibold flex items-center gap-1.5 hover:bg-accent hover:text-foreground rounded-full transition-colors disabled:opacity-50"
                  >
                    <c.Icon className="w-4 h-4" />
                    {isBusy ? "Applying…" : c.label}
                    {/* billable indicator: green dot if free, amber if billable */}
                    <span
                      className={`absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full border border-card ${
                        c.billable ? "bg-spark" : "bg-earth"
                      }`}
                      title={c.billable ? "Uses credits" : "Free tweak"}
                    />
                  </motion.button>
                );
              })}
            </nav>
          </motion.div>
        </main>

        {/* Right rail — swaps between Launch Setup and Visual Editor */}
        <AnimatePresence mode="wait">
          {selected ? (
            <VisualEditorPanel
              key="editor"
              selected={selected}
              onClose={() => setSelected(null)}
              onText={handleTextEdit}
              onFontSize={handleFontSizeStep}
              onColor={handleColor}
            />
          ) : (
            <LaunchSetupPanel
              key="setup"
              plan={plan}
              onGoLive={() => router.push("/publish")}
            />
          )}
        </AnimatePresence>
      </div>

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

      {/* Toast stack */}
      <div className="fixed top-20 right-6 z-[60] flex flex-col gap-2 pointer-events-none">
        <AnimatePresence>
          {toasts.map((t) => (
            <motion.div
              key={t.id}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className={`pointer-events-auto rounded-xl border shadow-lg px-4 py-3 max-w-sm ${
                t.kind === "success"
                  ? "bg-card border-border text-foreground"
                  : "bg-destructive/10 border-destructive/40 text-destructive"
              }`}
            >
              <div className="flex items-start gap-3">
                <div className="flex-1 text-sm">{t.message}</div>
                {t.snapshotId && t.slug && (
                  <button
                    onClick={() => handleUndo(t.slug!, t.snapshotId!)}
                    className="text-xs font-bold text-primary hover:underline flex items-center gap-1"
                  >
                    <Undo2 className="w-3 h-3" /> Undo
                  </button>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// LaunchSetupPanel — right rail when no element is selected
// ---------------------------------------------------------------------------

function LaunchSetupPanel({ plan, onGoLive }: { plan: PebblePlan | null; onGoLive: () => void }) {
  return (
    <motion.aside
      initial={{ opacity: 0, x: 8 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 8 }}
      transition={{ duration: 0.4 }}
      className="flex flex-col gap-3 p-4 w-[320px] bg-card border-l border-border overflow-y-auto"
    >
      <div className="mb-4 px-1">
        <h2 className="font-display text-xl font-semibold text-primary">Launch Setup</h2>
        <p className="text-xs text-muted-foreground opacity-70">
          {plan ? `${plan.setup_needs.filter((s) => s.status !== "auto").length} items remaining` : "Loading..."}
        </p>
      </div>
      <div className="space-y-2 flex-1">
        {plan?.setup_needs.map((s, i) => (
          <motion.div
            key={s.id}
            initial={{ opacity: 0, x: 8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.04 * i, duration: 0.3 }}
            className="p-3 rounded-lg bg-background border border-border flex flex-col gap-1"
            title={s.notes}
          >
            <div className="flex justify-between items-center">
              <span className="text-sm font-semibold">{s.label}</span>
              <span
                className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${
                  s.status === "auto"
                    ? "bg-earth/20 text-earth"
                    : s.status === "pending"
                      ? "bg-spark/15 text-spark"
                      : "bg-muted text-muted-foreground"
                }`}
              >
                {s.status === "auto" ? "Auto-done" : s.status === "pending" ? "Coming soon" : "You'll do this"}
              </span>
            </div>
          </motion.div>
        ))}
      </div>
      <div className="pt-3 mt-auto border-t border-border">
        <motion.button
          whileTap={{ scale: 0.97 }}
          onClick={onGoLive}
          className="w-full bg-secondary text-secondary-foreground py-3 rounded-xl font-bold flex items-center justify-center gap-2 hover:opacity-90 transition-opacity"
        >
          <Rocket className="w-4 h-4" /> Go Live
        </motion.button>
      </div>
    </motion.aside>
  );
}

// ---------------------------------------------------------------------------
// VisualEditorPanel — right rail when an element on the preview is selected
// ---------------------------------------------------------------------------

function VisualEditorPanel({
  selected,
  onClose,
  onText,
  onFontSize,
  onColor,
}: {
  selected: PebbleSelectMessage;
  onClose: () => void;
  onText: (newText: string) => void;
  onFontSize: (delta: number) => void;
  onColor: (hex: string) => void;
}) {
  const [textDraft, setTextDraft] = useState(selected.text);
  useEffect(() => { setTextDraft(selected.text); }, [selected]);

  const PALETTE = [
    "#1F1D1A", "#205661", "#4B6548", "#C76E3A", "#5A554E",
    "#F7F3EC", "#ECE6DC", "#D8D1C5", "#EFEAE1", "#FFFFFF",
  ];

  return (
    <motion.aside
      initial={{ opacity: 0, x: 16 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 16 }}
      transition={{ duration: 0.3 }}
      className="flex flex-col gap-4 p-5 w-[360px] bg-card border-l border-border overflow-y-auto"
    >
      <div className="flex justify-between items-start">
        <div>
          <p className="text-[10px] font-mono uppercase tracking-widest text-earth">Free style tweak ✨</p>
          <h2 className="font-display text-lg font-semibold text-primary mt-1">
            Editing {selected.tag.toUpperCase()}
          </h2>
        </div>
        <button
          onClick={onClose}
          className="w-8 h-8 rounded-full hover:bg-mist flex items-center justify-center"
          aria-label="Close editor"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Text editor — only show when the element actually has text content */}
      {selected.text && selected.text.trim() && (
        <div className="space-y-2">
          <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground flex items-center gap-1">
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
            className="w-full bg-primary text-primary-foreground py-2 rounded-lg text-sm font-semibold hover:opacity-90 transition-opacity disabled:opacity-40 flex items-center justify-center gap-2"
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
            className="flex-1 bg-background border border-border rounded-lg py-2 hover:bg-accent flex items-center justify-center gap-1 text-sm font-semibold"
          >
            <Minus className="w-4 h-4" /> Smaller
          </button>
          <button
            onClick={() => onFontSize(1)}
            className="flex-1 bg-background border border-border rounded-lg py-2 hover:bg-accent flex items-center justify-center gap-1 text-sm font-semibold"
          >
            <Plus className="w-4 h-4" /> Larger
          </button>
        </div>
        <p className="text-xs text-muted-foreground italic">Currently {selected.style.fontSize}</p>
      </div>

      {/* Color picker — Pebble palette */}
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
      </div>

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
        onClick={onClose}
        className="fixed inset-0 bg-charcoal/30 backdrop-blur-sm z-40"
      />
      <motion.aside
        initial={{ x: "100%" }}
        animate={{ x: 0 }}
        exit={{ x: "100%" }}
        transition={{ duration: 0.35, ease: [0.4, 0, 0.2, 1] }}
        className="fixed top-0 right-0 bottom-0 w-[440px] bg-card border-l border-border z-50 flex flex-col"
      >
        <div className="p-5 border-b border-border flex justify-between items-start">
          <div>
            <h2 className="font-display text-2xl font-semibold text-primary">Version history</h2>
            <p className="text-xs text-muted-foreground mt-1">
              Every change creates a snapshot. Roll back any time.
            </p>
          </div>
          <button
            onClick={onClose}
            className="w-9 h-9 rounded-full hover:bg-mist flex items-center justify-center"
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
              transition={{ delay: 0.04 * i, duration: 0.25 }}
              className="p-4 rounded-xl bg-background border border-border hover:border-primary/50 transition-colors"
            >
              <div className="flex justify-between items-start gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <ReasonBadge reason={s.reason} />
                    <span className="text-xs text-muted-foreground">
                      {formatTimestamp(s.written_at)}
                    </span>
                  </div>
                  <p className="text-sm text-foreground truncate">{s.source || s.reason}</p>
                  <p className="text-[11px] font-mono text-muted-foreground mt-1">
                    {s.files_count} files · {s.snapshot_id}
                  </p>
                </div>
                <button
                  onClick={() => onRollback(s.snapshot_id)}
                  className="flex items-center gap-1 bg-card border border-border text-foreground px-3 py-1.5 rounded-lg text-xs font-semibold hover:bg-accent transition-colors shrink-0"
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
      ? { bg: "bg-earth/20",      text: "text-earth",      label: reason.replace("visual-edit-", "") }
      : reason === "generate"
        ? { bg: "bg-primary/15",  text: "text-primary",    label: "Generated" }
        : reason === "restore"
          ? { bg: "bg-spark/15",  text: "text-spark",      label: "Restored" }
          : { bg: "bg-muted",     text: "text-muted-foreground", label: reason };
  return (
    <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${style.bg} ${style.text}`}>
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
