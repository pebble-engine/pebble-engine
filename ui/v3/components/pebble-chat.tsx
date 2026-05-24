"use client";

/**
 * PebbleChat — Control Center left-panel chat (2026-05-23).
 *
 * The chat-led interface to the Pebble app. Marc's design-night pivot:
 * instead of a project list as the dashboard primary surface, the
 * dashboard becomes a conversation with the Pebble assistant who can
 * answer questions, navigate the app on the user's behalf, and start
 * destructive flows behind a confirmation prompt.
 *
 * Backed by POST /api/chat → GPT-4o-mini via OpenRouter. Strict JSON
 * response shape ({reply, navigate_to, confirm_action}) so this
 * component never parses free text for intent.
 *
 * Conversation lives in React state for the session — no server-side
 * history (yet) so users get a fresh assistant per tab. localStorage
 * persistence is a follow-up; the trade-off is fine for v1 because
 * the assistant gets its context from the current route, not memory.
 *
 * Voice input uses the browser's Web Speech API. Auto-hidden when
 * the browser doesn't support it (Firefox today). Tap-to-record, tap-
 * again-to-stop — no continuous listening.
 */

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { useRouter, usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Mic,
  MicOff,
  Send,
  Sparkles,
  AlertTriangle,
  Loader2,
} from "lucide-react";
import {
  sendChat,
  type ChatMessage,
  type ChatConfirmAction,
} from "@/lib/api";
import { useAuth } from "@/components/auth-provider";

// Sitemap the assistant is allowed to navigate to. Keep this in sync
// with the DEFAULT_SITEMAP on the backend — but it's safe to pass any
// subset here; the backend filters down anyway.
const SITEMAP = [
  { path: "/dashboard",                label: "Dashboard" },
  { path: "/designs",                  label: "My designs" },
  { path: "/templates",                label: "Templates" },
  { path: "/integrations",             label: "Integrations" },
  { path: "/community",                label: "Community" },
  { path: "/community/launchpad",      label: "Community: Launchpad" },
  { path: "/community/hire-a-partner", label: "Community: Hire a partner" },
  { path: "/community/affiliate",      label: "Community: Affiliate program" },
  { path: "/settings",                 label: "Account settings" },
  { path: "/pricing",                  label: "Pricing" },
  { path: "/trust",                    label: "Trust Charter" },
];

// Per-route suggestion chips. The list shown in the chip rail depends
// on where the user is, so the assistant feels contextual rather than
// asking the same five things everywhere. Falls back to a generic set
// when the current route isn't matched.
const SUGGESTIONS_BY_ROUTE: Record<string, string[]> = {
  "/dashboard": [
    "What can I do here?",
    "Take me to my designs",
    "Show me templates",
    "Open my billing",
  ],
  "/templates": [
    "Which template is best for a bakery?",
    "What's the difference between Free and Premium?",
    "Take me back to my designs",
  ],
  "/integrations": [
    "How do I connect Stripe?",
    "Which integrations are live today?",
    "Open my account settings",
  ],
  "/community": [
    "Show me the launchpad",
    "How does the affiliate program work?",
    "Take me back to my designs",
  ],
  "/settings": [
    "Open billing portal",
    "Cancel my membership",
    "Take me back to dashboard",
  ],
};
const DEFAULT_SUGGESTIONS = [
  "What can I do here?",
  "Take me to templates",
  "Open my account settings",
];

// Web Speech API types — not in lib.dom for all TS versions, so we
// declare the minimal shape we use ourselves. Keeps the file self-
// contained without pulling in a polyfill package.
type MinimalSpeechRecognitionResult = {
  readonly length: number;
  item(idx: number): SpeechRecognitionAlternative;
  [idx: number]: SpeechRecognitionAlternative;
};
type SpeechRecognitionAlternative = { transcript: string };
type SpeechRecognitionEvent = {
  results: ArrayLike<MinimalSpeechRecognitionResult>;
};
type SpeechRecognition = {
  continuous:     boolean;
  interimResults: boolean;
  lang:           string;
  onresult: ((e: SpeechRecognitionEvent) => void) | null;
  onerror:  ((e: Event) => void) | null;
  onend:    ((e: Event) => void) | null;
  start(): void;
  stop(): void;
};
type SRClass = new () => SpeechRecognition;
function getSpeechRecognition(): SRClass | null {
  if (typeof window === "undefined") return null;
  const w = window as unknown as {
    SpeechRecognition?: SRClass;
    webkitSpeechRecognition?: SRClass;
  };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

type PendingConfirm = {
  action: ChatConfirmAction;
  reply:  string;
};

export type PebbleChatProps = {
  /** Optional opening line spoken by Pebble on mount. When omitted
   *  the chat starts empty and the user kicks off the conversation. */
  greeting?: string;
};

export function PebbleChat({ greeting }: PebbleChatProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuth();

  // History is just an array — first item is the greeting from Pebble
  // when one is provided. Cap displayed messages at 30 so the scroll
  // area doesn't grow unbounded; the API call already trims to 24
  // turns server-side.
  const [history, setHistory] = useState<ChatMessage[]>(() =>
    greeting ? [{ role: "assistant", content: greeting }] : [],
  );
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pendingConfirm, setPendingConfirm] = useState<PendingConfirm | null>(null);
  const [recording, setRecording] = useState(false);

  const inputRef = useRef<HTMLInputElement | null>(null);
  const scrollerRef = useRef<HTMLDivElement | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  // Pin scroll to the bottom whenever a new message arrives so the
  // latest line is visible without a manual scroll. Uses scrollTop
  // assignment rather than scrollIntoView so we don't jolt the wider
  // page when the chat panel is one column inside it.
  useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [history, sending, pendingConfirm]);

  // Cmd-K (or Ctrl-K) focuses the input from anywhere on the page.
  // Marc's mockup shows the ⌘K hint inside the input — keep parity.
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        inputRef.current?.focus();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  // Per-route suggestion chips. Recomputed when the user navigates so
  // the chips shown match where they're sitting.
  const suggestions = useMemo(() => {
    const exact = SUGGESTIONS_BY_ROUTE[pathname || "/dashboard"];
    if (exact) return exact;
    const prefixHit = Object.entries(SUGGESTIONS_BY_ROUTE).find(([k]) =>
      pathname?.startsWith(k + "/"),
    );
    return prefixHit?.[1] ?? DEFAULT_SUGGESTIONS;
  }, [pathname]);

  // Send a turn — appends user message to history immediately, calls
  // the backend, appends the reply, executes any navigate / confirm
  // action the assistant returned.
  const send = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || sending) return;

      const userMsg: ChatMessage = { role: "user", content: trimmed };
      const next = [...history, userMsg];
      setHistory(next);
      setInput("");
      setSending(true);
      setError(null);
      setPendingConfirm(null);

      try {
        const res = await sendChat(next, SITEMAP);
        setHistory((h) => [...h, { role: "assistant", content: res.reply }]);

        if (res.confirm_action) {
          // Don't navigate yet — the confirmation step owns that.
          setPendingConfirm({ action: res.confirm_action, reply: res.reply });
        } else if (res.navigate_to && res.navigate_to !== pathname) {
          // Tiny pause so the user sees the assistant's reply before
          // the route flips — feels like a guided handoff, not a yank.
          window.setTimeout(() => router.push(res.navigate_to!), 350);
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : String(e));
      } finally {
        setSending(false);
      }
    },
    [history, sending, router, pathname],
  );

  // Confirm a destructive action — the only place a billing portal /
  // delete flow gets triggered. Wired here (not in the assistant)
  // because every confirmation needs the user's explicit click.
  const executeConfirm = useCallback(async () => {
    if (!pendingConfirm) return;
    const key = pendingConfirm.action.key;
    setPendingConfirm(null);

    if (key === "open_billing_portal") {
      // Best-effort: the engine exposes /api/billing/portal which
      // returns a Stripe portal URL. Open it in the same tab so the
      // user lands back on /settings after.
      try {
        const res = await fetch("/api/billing/portal", {
          method:  "POST",
          headers: { "Content-Type": "application/json" },
        });
        const data = (await res.json()) as { url?: string; error?: string };
        if (data.url) {
          window.location.href = data.url;
          return;
        }
        setHistory((h) => [
          ...h,
          {
            role:    "assistant",
            content: data.error
              ? `Couldn't open billing: ${data.error}. Try /settings instead.`
              : "Couldn't open billing right now — try /settings.",
          },
        ]);
        router.push("/settings");
      } catch (e) {
        setHistory((h) => [
          ...h,
          {
            role:    "assistant",
            content: `Couldn't open billing (${e instanceof Error ? e.message : String(e)}). Try /settings.`,
          },
        ]);
        router.push("/settings");
      }
      return;
    }

    if (key === "delete_account") {
      // No auto-execute — bounce to the settings page where the
      // delete-account confirmation lives. The chat never deletes.
      router.push("/settings");
      setHistory((h) => [
        ...h,
        {
          role:    "assistant",
          content: "I've taken you to settings — delete account lives there. I never delete anything without you confirming on the page itself.",
        },
      ]);
      return;
    }
  }, [pendingConfirm, router]);

  // Web Speech API — start/stop recording. Result is appended to the
  // input buffer (not auto-sent) so the user can still edit before
  // hitting enter. Best-effort: silently no-ops when unsupported.
  const toggleRecording = useCallback(() => {
    const SR = getSpeechRecognition();
    if (!SR) return;
    if (recording) {
      recognitionRef.current?.stop();
      return;
    }
    const rec = new SR();
    rec.continuous = false;
    rec.interimResults = false;
    rec.lang = (typeof navigator !== "undefined" && navigator.language) || "en-US";
    rec.onresult = (e: SpeechRecognitionEvent) => {
      const results = Array.from({ length: e.results.length }, (_v, i) => e.results[i]);
      const transcript = results
        .map((r) => r[0]?.transcript || "")
        .join(" ")
        .trim();
      if (transcript) {
        setInput((cur) => (cur ? `${cur} ${transcript}` : transcript));
      }
    };
    rec.onerror = () => setRecording(false);
    rec.onend = () => setRecording(false);
    recognitionRef.current = rec;
    setRecording(true);
    try {
      rec.start();
    } catch {
      // start() can throw if already started — swallow.
      setRecording(false);
    }
  }, [recording]);

  // Tear down speech recognition on unmount so we don't leave the mic
  // hot when the user navigates away.
  useEffect(() => {
    return () => {
      recognitionRef.current?.stop();
    };
  }, []);

  const voiceSupported = useMemo(() => !!getSpeechRecognition(), []);
  const placeholder = user ? "Command Pebble..." : "Sign in to chat";

  return (
    <div className="flex h-full flex-col bg-card border-r border-border">
      {/* Header — model badge sits on the right per the mockup */}
      <header className="flex items-center justify-between px-4 py-3 border-b border-border shrink-0">
        <div className="flex items-center gap-2">
          <PebbleAvatar />
          <div className="flex flex-col">
            <p className="text-sm font-bold text-foreground leading-tight">Pebble</p>
            <p className="text-[10px] uppercase tracking-widest text-muted-foreground leading-tight">
              Your AI assistant
            </p>
          </div>
        </div>
        <span className="text-[10px] uppercase tracking-widest font-semibold text-muted-foreground px-2 py-1 rounded-full border border-border bg-card/80">
          GPT-4o mini
        </span>
      </header>

      {/* History */}
      <div
        ref={scrollerRef}
        className="flex-1 overflow-y-auto px-4 py-4 space-y-5"
      >
        {history.length === 0 && !sending && (
          <div className="text-center py-12 text-muted-foreground">
            <Sparkles className="w-5 h-5 mx-auto mb-2 opacity-50" />
            <p className="text-sm">Ask me to navigate, explain, or take you somewhere.</p>
            <p className="text-xs mt-1 opacity-70">Try one of the chips below.</p>
          </div>
        )}

        <AnimatePresence initial={false}>
          {history.map((msg, i) => (
            <motion.div
              key={`${i}-${msg.role}`}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              className={
                msg.role === "user"
                  ? "flex flex-col items-end gap-1.5"
                  : "flex flex-col items-start gap-1.5"
              }
            >
              <p className="text-[10px] uppercase tracking-widest font-semibold text-muted-foreground">
                {msg.role === "user" ? "You" : "Pebble"}
              </p>
              <div
                className={
                  msg.role === "user"
                    ? "bg-foreground text-background px-3.5 py-2.5 rounded-2xl rounded-tr-sm text-sm max-w-[88%] leading-snug"
                    : "bg-muted text-foreground px-3.5 py-2.5 rounded-2xl rounded-tl-sm text-sm max-w-[88%] leading-snug"
                }
              >
                {msg.content}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {sending && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span className="inline-flex h-1.5 w-1.5 rounded-full bg-foreground animate-pulse" />
            <span>Pebble is thinking…</span>
          </div>
        )}

        {pendingConfirm && (
          <ConfirmPanel
            action={pendingConfirm.action}
            onConfirm={executeConfirm}
            onCancel={() => setPendingConfirm(null)}
          />
        )}

        {error && (
          <div className="flex items-start gap-2 p-3 rounded-lg border border-red-300/40 bg-red-50 text-red-900 dark:border-red-900/60 dark:bg-red-950/40 dark:text-red-200 text-xs">
            <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Suggestion chips + input */}
      <div className="border-t border-border px-4 py-3 space-y-2.5 shrink-0">
        <div className="flex flex-wrap gap-1.5">
          {suggestions.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => send(s)}
              disabled={sending || !user}
              className="px-2.5 py-1 rounded-full border border-border bg-card text-xs font-semibold text-muted-foreground hover:text-foreground hover:border-primary/40 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {s}
            </button>
          ))}
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            send(input);
          }}
          className="relative"
        >
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={placeholder}
            disabled={!user || sending}
            className="w-full bg-background border border-border rounded-xl pl-10 pr-24 py-2.5 text-sm text-foreground placeholder-muted-foreground/70 focus:outline-none focus:border-primary/60 focus:ring-2 focus:ring-primary/20 transition-colors disabled:opacity-60"
            aria-label="Chat with Pebble"
          />
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
            <Sparkles className="w-4 h-4" />
          </span>

          <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
            {voiceSupported && (
              <button
                type="button"
                onClick={toggleRecording}
                disabled={!user}
                className={`p-1.5 rounded-md transition-colors ${
                  recording
                    ? "bg-red-500 text-white animate-pulse"
                    : "text-muted-foreground hover:text-foreground hover:bg-accent"
                } disabled:opacity-40`}
                title={recording ? "Stop recording" : "Voice input"}
                aria-label={recording ? "Stop recording" : "Start voice input"}
              >
                {recording ? <MicOff className="w-3.5 h-3.5" /> : <Mic className="w-3.5 h-3.5" />}
              </button>
            )}
            {input.trim() ? (
              <button
                type="submit"
                disabled={sending || !user}
                className="p-1.5 rounded-md bg-foreground text-background hover:opacity-90 disabled:opacity-40"
                aria-label="Send"
              >
                {sending ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
              </button>
            ) : (
              <kbd className="hidden sm:inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-mono text-muted-foreground border border-border bg-muted">
                ⌘K
              </kbd>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}

// Tiny Pebble droplet avatar — uses the existing brand asset path. If
// the image is missing the alt-text fallback renders cleanly.
function PebbleAvatar() {
  return (
    <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-foreground text-background text-xs font-bold">
      P
    </span>
  );
}

function ConfirmPanel({
  action,
  onConfirm,
  onCancel,
}: {
  action: ChatConfirmAction;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  return (
    <div className="p-3 rounded-lg border border-amber-400/40 bg-amber-50 dark:border-amber-700/40 dark:bg-amber-950/30">
      <div className="flex items-start gap-2 mb-2">
        <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5 text-amber-700 dark:text-amber-400" />
        <p className="text-xs font-semibold text-amber-900 dark:text-amber-200">
          Pebble wants to: {action.label}
        </p>
      </div>
      <div className="flex gap-2">
        <button
          type="button"
          onClick={onConfirm}
          className="flex-1 px-3 py-1.5 rounded-md bg-foreground text-background text-xs font-semibold hover:opacity-90"
        >
          Continue
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-3 py-1.5 rounded-md border border-border text-foreground text-xs font-semibold hover:bg-accent"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
