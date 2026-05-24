"use client";

/**
 * PebbleChat — the Control Center chat panel (2026-05-23, rev 2).
 *
 * The chat-led interface to the Pebble app. Three modes via bottom
 * tabs:
 *   - Chat      — multi-turn conversation with Peblet (GPT-4o-mini)
 *   - Shortcuts — one-tap actions (Navigate / Build / Manage)
 *   - Docs      — searchable help index, with fallback to "Ask Peblet"
 *
 * Hero Peblet mascot at the top is shared across all three tabs so
 * the assistant identity stays present even when the user is browsing
 * shortcuts. Greeting only renders on the Chat tab.
 *
 * Backed by POST /api/chat. Strict JSON response shape (reply,
 * navigate_to, confirm_action). Navigation auto-fires on a 350ms
 * delay so the user reads the reply first; destructive intents wait
 * for an explicit confirm tap.
 *
 * Voice input via Web Speech API — auto-hidden on browsers without
 * support (Firefox today). Tap-to-record, transcript appends to the
 * input buffer rather than auto-sending so the user can edit first.
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
  MessageSquare,
  Zap,
  BookOpen,
} from "lucide-react";
import {
  sendChat,
  type ChatMessage,
  type ChatConfirmAction,
} from "@/lib/api";
import { useAuth } from "@/components/auth-provider";
import { PebletMascot } from "@/components/peblet-mascot";
import { PebletShortcuts } from "@/components/peblet-shortcuts";
import { PebletDocs } from "@/components/peblet-docs";

// Web Speech API minimal types — TS lib.dom doesn't ship these for
// all versions, so we declare the subset we use ourselves.
type MinimalSpeechRecognitionResult = {
  readonly length: number;
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

const SITEMAP = [
  { path: "/dashboard",                label: "Dashboard" },
  { path: "/projects",                 label: "Projects" },
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

const SUGGESTIONS_BY_ROUTE: Record<string, string[]> = {
  "/dashboard":    ["Help me build a landing page", "Make design changes", "How do I connect a domain?", "Show me my projects"],
  "/projects":     ["Open my newest project", "How do I publish a site?", "Where's the version history?"],
  "/templates":    ["Which template is best for a bakery?", "Free vs Premium?", "Take me back to my projects"],
  "/integrations": ["How do I connect Stripe?", "Which integrations are live today?", "Open my account settings"],
  "/community":    ["Show me the launchpad", "How does the affiliate program work?", "Take me back to my projects"],
  "/settings":     ["Open billing portal", "Cancel my membership", "Take me back to dashboard"],
};
const DEFAULT_SUGGESTIONS = ["What can I do here?", "Take me to templates", "Open my account settings"];

type PendingConfirm = { action: ChatConfirmAction; reply: string };
type Tab = "chat" | "shortcuts" | "docs";

export type PebbleChatProps = {
  greeting?: string;
};

export function PebbleChat({ greeting }: PebbleChatProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuth();

  const [tab, setTab] = useState<Tab>("chat");
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

  useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [history, sending, pendingConfirm]);

  // Cmd-K (or Ctrl-K) focuses the chat input and switches to the
  // Chat tab from anywhere — matches the kbd hint in the input.
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setTab("chat");
        // requestAnimationFrame so the input is mounted before focus.
        requestAnimationFrame(() => inputRef.current?.focus());
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const suggestions = useMemo(() => {
    const exact = SUGGESTIONS_BY_ROUTE[pathname || "/dashboard"];
    if (exact) return exact;
    const prefixHit = Object.entries(SUGGESTIONS_BY_ROUTE).find(([k]) =>
      pathname?.startsWith(k + "/"),
    );
    return prefixHit?.[1] ?? DEFAULT_SUGGESTIONS;
  }, [pathname]);

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
          setPendingConfirm({ action: res.confirm_action, reply: res.reply });
        } else if (res.navigate_to && res.navigate_to !== pathname) {
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

  // Handler the Docs tab uses to hand a query off to chat — switches
  // tab + sends the question in one step.
  const handleAskInChat = useCallback(
    (question: string) => {
      setTab("chat");
      void send(question);
    },
    [send],
  );

  const executeConfirm = useCallback(async () => {
    if (!pendingConfirm) return;
    const key = pendingConfirm.action.key;
    setPendingConfirm(null);

    if (key === "open_billing_portal") {
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
          { role: "assistant", content: data.error ? `Couldn't open billing: ${data.error}. Try /settings instead.` : "Couldn't open billing right now — try /settings." },
        ]);
        router.push("/settings");
      } catch (e) {
        setHistory((h) => [
          ...h,
          { role: "assistant", content: `Couldn't open billing (${e instanceof Error ? e.message : String(e)}). Try /settings.` },
        ]);
        router.push("/settings");
      }
      return;
    }

    if (key === "delete_account") {
      router.push("/settings");
      setHistory((h) => [
        ...h,
        { role: "assistant", content: "I've taken you to settings — delete account lives there. I never delete anything without you confirming on the page itself." },
      ]);
      return;
    }
  }, [pendingConfirm, router]);

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
      const transcript = results.map((r) => r[0]?.transcript || "").join(" ").trim();
      if (transcript) setInput((cur) => (cur ? `${cur} ${transcript}` : transcript));
    };
    rec.onerror = () => setRecording(false);
    rec.onend = () => setRecording(false);
    recognitionRef.current = rec;
    setRecording(true);
    try {
      rec.start();
    } catch {
      setRecording(false);
    }
  }, [recording]);

  useEffect(() => {
    return () => { recognitionRef.current?.stop(); };
  }, []);

  const voiceSupported = useMemo(() => !!getSpeechRecognition(), []);

  return (
    <div className="flex h-full flex-col bg-card border-l border-border">
      {/* Hero — Peblet mascot + identity. Shared across all tabs so
          the assistant's presence stays anchored. */}
      <header className="flex flex-col items-center text-center px-4 pt-5 pb-4 border-b border-border shrink-0 bg-gradient-to-b from-primary/8 to-transparent">
        <div className="flex items-center justify-between w-full mb-2">
          <div className="flex items-center gap-1.5">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <p className="text-sm font-bold text-foreground leading-none">Peblet</p>
          </div>
          <span className="text-[10px] uppercase tracking-widest font-semibold text-muted-foreground px-2 py-0.5 rounded-full border border-border">
            AI Assistant
          </span>
        </div>
        <PebletMascot size="lg" animate />
        <div className="mt-3 space-y-1">
          <p className="text-base font-bold text-foreground">
            Hi{user ? "" : " there"}! I&apos;m Peblet <span className="inline-block">👋</span>
          </p>
          <p className="text-xs text-muted-foreground leading-snug max-w-[260px]">
            Your personal AI assistant for building and managing your website.
          </p>
        </div>
      </header>

      {/* Tab content area — only one mounted at a time so search /
          chat / shortcuts state is reset cleanly when you switch. */}
      <div className="flex-1 min-h-0 flex flex-col">
        {tab === "chat" && (
          <ChatTab
            history={history}
            sending={sending}
            error={error}
            pendingConfirm={pendingConfirm}
            scrollerRef={scrollerRef}
            inputRef={inputRef}
            input={input}
            setInput={setInput}
            send={send}
            suggestions={suggestions}
            voiceSupported={voiceSupported}
            recording={recording}
            toggleRecording={toggleRecording}
            user={user}
            executeConfirm={executeConfirm}
            cancelConfirm={() => setPendingConfirm(null)}
          />
        )}
        {tab === "shortcuts" && <PebletShortcuts />}
        {tab === "docs"      && <PebletDocs onAskInChat={handleAskInChat} />}
      </div>

      {/* Bottom tab rail — Chat / Shortcuts / Docs. Always visible
          so users can flip modes without leaving the panel. */}
      <nav className="grid grid-cols-3 border-t border-border shrink-0">
        <TabButton active={tab === "chat"}      onClick={() => setTab("chat")}      Icon={MessageSquare} label="Chat" />
        <TabButton active={tab === "shortcuts"} onClick={() => setTab("shortcuts")} Icon={Zap}           label="Shortcuts" />
        <TabButton active={tab === "docs"}      onClick={() => setTab("docs")}      Icon={BookOpen}      label="Docs" />
      </nav>
    </div>
  );
}

// ─── Chat tab body ────────────────────────────────────────────────────── //

type AuthUser = ReturnType<typeof useAuth>["user"];

function ChatTab(props: {
  history: ChatMessage[];
  sending: boolean;
  error: string | null;
  pendingConfirm: PendingConfirm | null;
  scrollerRef: React.RefObject<HTMLDivElement | null>;
  inputRef: React.RefObject<HTMLInputElement | null>;
  input: string;
  setInput: (v: string) => void;
  send: (text: string) => void | Promise<void>;
  suggestions: string[];
  voiceSupported: boolean;
  recording: boolean;
  toggleRecording: () => void;
  user: AuthUser;
  executeConfirm: () => void | Promise<void>;
  cancelConfirm: () => void;
}) {
  const {
    history, sending, error, pendingConfirm,
    scrollerRef, inputRef, input, setInput, send,
    suggestions, voiceSupported, recording, toggleRecording,
    user, executeConfirm, cancelConfirm,
  } = props;

  const placeholder = user ? "Ask me anything..." : "Sign in to chat";

  return (
    <div className="flex-1 min-h-0 flex flex-col">
      {/* History */}
      <div ref={scrollerRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        <AnimatePresence initial={false}>
          {history.map((msg, i) => (
            <motion.div
              key={`${i}-${msg.role}`}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              className={msg.role === "user" ? "flex flex-col items-end gap-1" : "flex flex-col items-start gap-1"}
            >
              <p className="text-[10px] uppercase tracking-widest font-semibold text-muted-foreground">
                {msg.role === "user" ? "You" : "Peblet"}
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
            <span>Peblet is thinking…</span>
          </div>
        )}

        {pendingConfirm && (
          <ConfirmPanel
            action={pendingConfirm.action}
            onConfirm={executeConfirm}
            onCancel={cancelConfirm}
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
        <div className="flex flex-col gap-1.5">
          {suggestions.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => send(s)}
              disabled={sending || !user}
              className="w-full text-left flex items-center gap-2 px-3 py-2 rounded-lg border border-border bg-card text-xs font-semibold text-foreground hover:border-primary/40 hover:bg-accent transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <MessageSquare className="w-3.5 h-3.5 text-muted-foreground shrink-0" />
              <span className="flex-1 truncate">{s}</span>
            </button>
          ))}
        </div>

        <form
          onSubmit={(e) => { e.preventDefault(); void send(input); }}
          className="relative"
        >
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={placeholder}
            disabled={!user || sending}
            className="w-full bg-background border border-border rounded-xl pl-3 pr-20 py-2.5 text-sm text-foreground placeholder-muted-foreground/70 focus:outline-none focus:border-primary/60 focus:ring-2 focus:ring-primary/20 transition-colors disabled:opacity-60"
            aria-label="Chat with Peblet"
          />

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
            <button
              type="submit"
              disabled={sending || !user || !input.trim()}
              className="p-1.5 rounded-md bg-primary text-primary-foreground hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed"
              aria-label="Send"
            >
              {sending ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─── Tab button ─────────────────────────────────────────────────────── //

function TabButton({
  active, onClick, Icon, label,
}: {
  active: boolean;
  onClick: () => void;
  Icon: typeof MessageSquare;
  label: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex flex-col items-center gap-1 py-2.5 text-xs font-semibold transition-colors ${
        active
          ? "text-primary bg-primary/5"
          : "text-muted-foreground hover:text-foreground hover:bg-accent"
      }`}
    >
      <Icon className="w-4 h-4" />
      {label}
    </button>
  );
}

// ─── Destructive-action confirm panel ───────────────────────────────── //

function ConfirmPanel({
  action, onConfirm, onCancel,
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
          Peblet wants to: {action.label}
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
