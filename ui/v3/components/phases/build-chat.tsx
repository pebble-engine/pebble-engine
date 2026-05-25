"use client";

/**
 * BuildChatPanel — Phase 58a (2026-05-22).
 *
 * A chat panel that pops up during the draft phase and keeps the user
 * engaged by asking 3 targeted questions while the engine builds in
 * the background. Answers are collected and fed back to the engine via
 * /api/enrich-content immediately after the build finishes, so the site
 * gets personalised details (phone, services, location) without the user
 * having to wait for a second full build.
 *
 * Layout: shown in the LEFT column on md+ screens. Hidden on mobile
 * (the build status is already a lot of content on a phone screen).
 *
 * Question timing: tied to real SSE events so questions feel responsive
 * ("we just figured out your industry, quick — what's your phone?").
 * Each question appears ~800ms after the trigger event to feel natural.
 */

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Check } from "lucide-react";
import type { SSEEvent } from "@/lib/api";
import { EASE_CINEMATIC, SHORT_S } from "@/lib/motion";

/* ---------- Question bank ------------------------------------------------ */

export type CollectedAnswer = {
  questionId: string;
  question:   string;
  answer:     string;
};

type Question = {
  id:          string;
  text:        string;
  /** SSE event type that triggers this question to appear. */
  trigger:     SSEEvent["type"];
  placeholder: string;
};

const QUESTIONS: Question[] = [
  {
    id:          "phone",
    trigger:     "industry",
    text:        "What phone number should we put on your site?",
    placeholder: "e.g. (555) 123-4567",
  },
  {
    id:          "services",
    trigger:     "style",
    text:        "Any 2–3 services you most want to highlight?",
    placeholder: "e.g. Oil changes, Brake repair, Tire rotation",
  },
  {
    id:          "location",
    trigger:     "generating",
    text:        "What city or area do you primarily serve?",
    placeholder: "e.g. Brooklyn, NY",
  },
];

/* ---------- Message types ------------------------------------------------ */

type Msg = {
  role:        "pebble" | "user";
  text:        string;
  /** Set on Pebble messages that ARE a question — used to match answers. */
  questionId?: string;
};

/* ---------- Props -------------------------------------------------------- */

interface Props {
  sseEvents:          SSEEvent[];
  done:               boolean;
  error:              string | null;
  /** Called when the build finishes. Passes whatever the user answered. */
  onAnswers:          (answers: CollectedAnswer[]) => void;
}

/* ========================================================================= */

export function BuildChatPanel({ sseEvents, done, error, onAnswers }: Props) {
  const [messages, setMessages] = useState<Msg[]>([
    {
      role: "pebble",
      text: "Hi! I'm Pebblebot 👋 While your site builds I'll grab a few quick details to personalise it — nothing required, just answer what you know.",
    },
  ]);
  const [input, setInput]           = useState("");
  const [answers, setAnswers]       = useState<CollectedAnswer[]>([]);
  // askedIds was useState before — but it's a write-only accumulator
  // (never read for rendering), and the previous code had a stale-
  // closure bug where two SSE events arriving in quick succession could
  // both see a snapshot before either had added its question, and
  // double-ask. Moving to a ref guarantees we always read the latest
  // value at check time. Bonus: no useless re-renders on every add.
  const askedIdsRef                 = useRef<Set<string>>(new Set());
  const [isTyping, setIsTyping]     = useState(false);
  const bottomRef                   = useRef<HTMLDivElement>(null);
  const inputRef                    = useRef<HTMLInputElement>(null);
  const answeredRef                 = useRef(false);

  /* Auto-scroll on new messages */
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  /* Trigger questions from SSE events */
  useEffect(() => {
    if (!sseEvents.length) return;
    const latest = sseEvents[sseEvents.length - 1];
    for (const q of QUESTIONS) {
      if (q.trigger !== latest.type) continue;
      // Atomic check-and-add on the ref guarantees a question is only
      // queued ONCE even if two SSE events with the same trigger fire
      // before either has finished its 900ms typing animation.
      if (askedIdsRef.current.has(q.id)) continue;
      askedIdsRef.current.add(q.id);
      setIsTyping(true);
      setTimeout(() => {
        setIsTyping(false);
        setMessages((prev) => [
          ...prev,
          { role: "pebble", text: q.text, questionId: q.id },
        ]);
        inputRef.current?.focus();
      }, 900);
      break;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sseEvents]);

  /* Notify parent when build is done */
  useEffect(() => {
    if (done && !answeredRef.current) {
      answeredRef.current = true;
      onAnswers(answers);
    }
  }, [done, answers, onAnswers]);

  function handleSend() {
    const text = input.trim();
    if (!text) return;

    /* Find the most recent unanswered Pebble question */
    const lastQ = [...messages]
      .reverse()
      .find((m) => m.role === "pebble" && m.questionId);

    setMessages((prev) => [...prev, { role: "user", text }]);
    setInput("");

    if (lastQ?.questionId) {
      const q = QUESTIONS.find((q) => q.id === lastQ.questionId);
      if (q) {
        const answer: CollectedAnswer = {
          questionId: q.id,
          question:   q.text,
          answer:     text,
        };
        setAnswers((prev) => [...prev, answer]);

        /* Ack + optional next nudge */
        setIsTyping(true);
        setTimeout(() => {
          setIsTyping(false);
          const remaining = QUESTIONS.filter(
            (q) => !askedIdsRef.current.has(q.id),
          ).length;
          const ack =
            remaining > 0
              ? "Got it! I'll weave that in ✓"
              : "Perfect — that's all I need. Finishing your site now!";
          setMessages((prev) => [...prev, { role: "pebble", text: ack }]);
        }, 500);
      }
    }
  }

  const allDone = done || !!error;

  return (
    <div className="flex flex-col h-full rounded-2xl border border-border bg-card overflow-hidden shadow-sm">
      {/* Header */}
      <div className="flex items-center gap-2.5 px-4 py-3 border-b border-border shrink-0">
        <div className="w-8 h-8 rounded-full bg-[#3054ff] flex items-center justify-center text-white text-xs font-bold shrink-0">
          P
        </div>
        <div className="min-w-0">
          <p className="text-sm font-bold text-foreground leading-none">Pebblebot</p>
          <p className="text-[11px] text-muted-foreground mt-0.5">personalising while building</p>
        </div>
        <AnimatePresence>
          {!allDone && (
            <motion.span
              key="building"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="ml-auto text-[11px] font-mono text-[#3054ff] bg-[#3054ff]/8 px-2 py-0.5 rounded-full"
            >
              building…
            </motion.span>
          )}
          {allDone && !error && (
            <motion.span
              key="done"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              className="ml-auto text-[11px] font-mono text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20 px-2 py-0.5 rounded-full flex items-center gap-1"
            >
              <Check className="w-3 h-3" /> done
            </motion.span>
          )}
        </AnimatePresence>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3 min-h-0">
        {messages.map((msg, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: SHORT_S, ease: EASE_CINEMATIC }}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[88%] px-3 py-2 text-sm leading-snug rounded-2xl ${
                msg.role === "user"
                  ? "bg-[#3054ff] text-white rounded-br-md"
                  : "bg-muted text-foreground rounded-bl-md"
              }`}
            >
              {msg.text}
            </div>
          </motion.div>
        ))}

        {/* Typing indicator */}
        <AnimatePresence>
          {isTyping && (
            <motion.div
              key="typing"
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="flex justify-start"
            >
              <div className="bg-muted rounded-2xl rounded-bl-md px-3 py-2.5 flex gap-1 items-center">
                {[0, 1, 2].map((i) => (
                  <motion.span
                    key={i}
                    className="w-1.5 h-1.5 rounded-full bg-muted-foreground/60"
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{ duration: 1, delay: i * 0.2, repeat: Infinity }}
                  />
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Build-done ack */}
        <AnimatePresence>
          {done && answers.length > 0 && (
            <motion.div
              key="done-msg"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: SHORT_S, delay: 0.3 }}
              className="flex justify-start"
            >
              <div className="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-2xl rounded-bl-md px-3 py-2 text-sm text-emerald-700 dark:text-emerald-400">
                ✓ Applying your details to the site now…
              </div>
            </motion.div>
          )}
          {done && answers.length === 0 && (
            <motion.div
              key="done-no-answers"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-start"
            >
              <div className="bg-muted rounded-2xl rounded-bl-md px-3 py-2 text-sm text-muted-foreground">
                Your site is ready — you can always edit details later.
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <AnimatePresence>
        {!allDone && (
          <motion.div
            key="input"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="px-3 py-3 border-t border-border flex gap-2 shrink-0"
          >
            <input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
              placeholder="Type your answer…"
              className="flex-1 bg-muted rounded-xl px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground outline-none focus:ring-2 focus:ring-[#3054ff] transition-shadow"
            />
            <button
              type="button"
              onClick={handleSend}
              disabled={!input.trim()}
              aria-label="Send"
              className="w-9 h-9 rounded-xl bg-[#3054ff] text-white flex items-center justify-center disabled:opacity-30 hover:bg-[#2545e8] transition-colors shrink-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#3054ff]"
            >
              <Send className="w-4 h-4" />
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
