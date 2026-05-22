"use client";

/**
 * IntegrationsPhase — Phase 56a (2026-05-22).
 *
 * Replaces the "Features" placeholder in the workspace rail.
 * Shows 6 one-click integration cards:
 *   - WhatsApp chat bubble
 *   - Booking link button (Calendly / Cal.com / any URL)
 *   - Google Maps embed
 *   - Social links rail (Instagram, Facebook, TikTok, X, LinkedIn)
 *   - Cookie-consent banner
 *   - Custom code injection
 *
 * Each card has a toggle; enabling reveals a small config form.
 * On save, calls /api/projects/<slug>/integrations and the engine
 * injects the widget HTML into the preview instantly (no rebuild).
 *
 * Design choices
 * --------------
 * - 2-column grid on md+, single column on mobile.
 * - Cards are compact — just enough to show the widget is alive.
 * - "Live in preview" badge appears after a successful save.
 * - No plan gating — integrations are available on Free too.
 */

import React, { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  MessageCircle,
  CalendarCheck,
  MapPin,
  Share2,
  Cookie,
  Code2,
  Check,
  ChevronDown,
  ChevronUp,
  Loader2,
  AlertCircle,
} from "lucide-react";
import {
  getIntegrations,
  saveIntegration,
  deleteIntegration,
  type IntegrationId,
  type IntegrationRecord,
  type IntegrationsMap,
} from "@/lib/api";
import { getLastBuild } from "@/lib/state";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";
import { fadeUp, SHORT_S, EASE_CINEMATIC, withReducedMotion } from "@/lib/motion";

// ---------------------------------------------------------------------------
// Integration catalogue — drives the UI
// ---------------------------------------------------------------------------

type FieldDef = {
  key:          string;
  label:        string;
  placeholder:  string;
  type?:        "text" | "url" | "tel" | "textarea";
  required?:    boolean;
};

type IntegrationDef = {
  id:          IntegrationId;
  icon:        React.ElementType;
  name:        string;
  description: string;
  iconBg:      string;
  fields:      FieldDef[];
};

const INTEGRATIONS: IntegrationDef[] = [
  {
    id:          "whatsapp",
    icon:        MessageCircle,
    name:        "WhatsApp Chat",
    description: "A floating chat bubble links visitors directly to your WhatsApp. Great for service businesses.",
    iconBg:      "bg-[#25D366]/15",
    fields: [
      { key: "phone",   label: "Your WhatsApp number", placeholder: "+1 555 123 4567", type: "tel", required: true },
      { key: "message", label: "Pre-filled message (optional)", placeholder: "Hi! I'd like to learn more about your services." },
    ],
  },
  {
    id:          "booking",
    icon:        CalendarCheck,
    name:        "Booking Button",
    description: "A fixed 'Book a call' button. Paste any Calendly, Cal.com, or scheduling URL.",
    iconBg:      "bg-primary/10",
    fields: [
      { key: "url",         label: "Booking URL", placeholder: "https://calendly.com/yourname/30min", type: "url", required: true },
      { key: "button_text", label: "Button label", placeholder: "Book a call" },
    ],
  },
  {
    id:          "google-maps",
    icon:        MapPin,
    name:        "Google Maps",
    description: "Embed a map so visitors can find your location. Just enter your business address.",
    iconBg:      "bg-[#EA4335]/10",
    fields: [
      { key: "address", label: "Business address", placeholder: "123 Main St, Brooklyn, NY 11201", required: true },
    ],
  },
  {
    id:          "social",
    icon:        Share2,
    name:        "Social Links",
    description: "A vertical icon rail linking to your social profiles. Leave blank any you don't use.",
    iconBg:      "bg-[#E1306C]/10",
    fields: [
      { key: "instagram", label: "Instagram URL",  placeholder: "https://instagram.com/yourhandle", type: "url" },
      { key: "facebook",  label: "Facebook URL",   placeholder: "https://facebook.com/yourpage",    type: "url" },
      { key: "tiktok",    label: "TikTok URL",     placeholder: "https://tiktok.com/@yourhandle",   type: "url" },
      { key: "x",         label: "X (Twitter) URL",placeholder: "https://x.com/yourhandle",         type: "url" },
      { key: "linkedin",  label: "LinkedIn URL",   placeholder: "https://linkedin.com/in/you",      type: "url" },
    ],
  },
  {
    id:          "cookie-consent",
    icon:        Cookie,
    name:        "Cookie Consent",
    description: "A minimal GDPR-friendly cookie notice. Visitors dismiss it once and it stays gone.",
    iconBg:      "bg-amber-500/10",
    fields: [
      { key: "message",     label: "Banner message",      placeholder: "We use cookies to improve your experience." },
      { key: "privacy_url", label: "Privacy policy URL",  placeholder: "/privacy", type: "url" },
    ],
  },
  {
    id:          "custom-code",
    icon:        Code2,
    name:        "Custom Code",
    description: "Paste any HTML/JS snippet (Tidio chat, Tag Manager, Hotjar, etc.). Injected before </body>.",
    iconBg:      "bg-muted",
    fields: [
      { key: "code", label: "HTML / script code", placeholder: "<!-- e.g. <script src='...'></script> -->", type: "textarea" },
    ],
  },
];

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

type CardState = "idle" | "saving" | "saved" | "error";

function IntegrationCard({
  def,
  record,
  onSave,
  onRemove,
}: {
  def:      IntegrationDef;
  record:   IntegrationRecord | undefined;
  onSave:   (id: IntegrationId, enabled: boolean, config: Record<string, string>) => Promise<void>;
  onRemove: (id: IntegrationId) => Promise<void>;
}) {
  const isEnabled = record?.enabled ?? false;
  const [expanded, setExpanded] = useState(isEnabled);
  const [state, setState] = useState<CardState>("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Local config state — seed from saved record
  const [config, setConfig] = useState<Record<string, string>>(
    (record?.config as Record<string, string>) ?? {},
  );

  // Sync expansion when record changes (e.g. after load)
  useEffect(() => {
    setExpanded(isEnabled);
    if (record?.config) setConfig(record.config as Record<string, string>);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isEnabled]);

  const Icon = def.icon;

  async function handleToggle() {
    const next = !isEnabled;
    setExpanded(next);
    if (!next) {
      // Disable immediately
      setState("saving");
      try {
        await onRemove(def.id);
        setState("idle");
      } catch {
        setState("error");
        setErrorMsg("Couldn't disable. Try again.");
      }
    }
  }

  async function handleSave() {
    // Validate required fields
    for (const f of def.fields) {
      if (f.required && !(config[f.key] || "").trim()) {
        setErrorMsg(`${f.label} is required.`);
        setState("error");
        return;
      }
    }
    setState("saving");
    setErrorMsg(null);
    try {
      await onSave(def.id, true, config);
      setState("saved");
      setTimeout(() => setState("idle"), 2500);
    } catch (e) {
      setState("error");
      setErrorMsg(e instanceof Error ? e.message : "Couldn't save. Try again.");
    }
  }

  const showSaved = state === "saved";

  return (
    <motion.div
      layout
      className={`rounded-2xl border transition-colors ${
        isEnabled
          ? "border-primary/40 bg-primary/5"
          : "border-border bg-card"
      }`}
    >
      {/* Card header — always visible */}
      <div className="flex items-start gap-3 p-5">
        <span className={`flex-shrink-0 inline-flex h-10 w-10 items-center justify-center rounded-xl ${def.iconBg}`}>
          <Icon className="h-5 w-5 text-foreground/70" aria-hidden="true" />
        </span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className={`${type.heading.s} text-foreground`}>{def.name}</h3>
            {isEnabled && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-primary text-primary-foreground text-[9px] font-bold uppercase tracking-widest">
                <Check className="w-2.5 h-2.5" /> Live
              </span>
            )}
          </div>
          <p className={`${type.body.s} text-muted-foreground mt-0.5 leading-relaxed`}>
            {def.description}
          </p>
        </div>
        {/* Toggle */}
        <button
          onClick={handleToggle}
          aria-pressed={isEnabled}
          aria-label={isEnabled ? `Disable ${def.name}` : `Enable ${def.name}`}
          className={`flex-shrink-0 relative inline-flex h-6 w-11 cursor-pointer rounded-full border-2 border-transparent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
            isEnabled ? "bg-primary" : "bg-muted"
          }`}
        >
          <span
            className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-lg transition-transform ${
              isEnabled ? "translate-x-5" : "translate-x-0"
            }`}
          />
        </button>
      </div>

      {/* Expandable config form */}
      <AnimatePresence initial={false}>
        {expanded && (
          <motion.div
            key="form"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: SHORT_S, ease: EASE_CINEMATIC }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 space-y-3 border-t border-border/50 pt-4">
              {def.fields.map((field) => (
                <div key={field.key} className="space-y-1">
                  <label className={`${type.eyebrow} block`}>
                    {field.label}
                    {field.required && <span className="text-destructive ml-0.5">*</span>}
                  </label>
                  {field.type === "textarea" ? (
                    <textarea
                      rows={4}
                      value={config[field.key] ?? ""}
                      onChange={(e) => setConfig((p) => ({ ...p, [field.key]: e.target.value }))}
                      placeholder={field.placeholder}
                      className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-ring resize-y"
                    />
                  ) : (
                    <input
                      type={field.type ?? "text"}
                      value={config[field.key] ?? ""}
                      onChange={(e) => setConfig((p) => ({ ...p, [field.key]: e.target.value }))}
                      placeholder={field.placeholder}
                      className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                    />
                  )}
                </div>
              ))}

              {errorMsg && (
                <p className="flex items-center gap-1.5 text-xs text-destructive">
                  <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
                  {errorMsg}
                </p>
              )}

              <button
                onClick={handleSave}
                disabled={state === "saving"}
                className={`${interactions.button} w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-bold transition-colors ${
                  showSaved
                    ? "bg-green-600 text-white"
                    : "bg-primary text-primary-foreground"
                } disabled:opacity-50`}
              >
                {state === "saving" && <Loader2 className="w-4 h-4 animate-spin" />}
                {showSaved && <Check className="w-4 h-4" />}
                {state === "saving" ? "Applying…"
                  : showSaved ? "Applied to preview ✓"
                  : "Apply to site"}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

type Props = {
  onBack: () => void;
};

export function IntegrationsPhase({ onBack }: Props) {
  const build = getLastBuild();
  const slug = build?.slug ?? null;

  const [integrations, setIntegrations] = useState<IntegrationsMap>({});
  const [loading, setLoading] = useState(true);

  const safeMotion = withReducedMotion(fadeUp);

  // Load saved integrations on mount
  useEffect(() => {
    if (!slug) { setLoading(false); return; }
    getIntegrations(slug)
      .then((data) => setIntegrations(data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [slug]);

  async function handleSave(
    id: IntegrationId,
    enabled: boolean,
    config: Record<string, string>,
  ) {
    if (!slug) throw new Error("No active project");
    const saved = await saveIntegration(slug, id, enabled, config);
    setIntegrations((prev) => ({ ...prev, [id]: { enabled: saved.enabled, config: saved.config } }));
  }

  async function handleRemove(id: IntegrationId) {
    if (!slug) throw new Error("No active project");
    await deleteIntegration(slug, id);
    setIntegrations((prev) => {
      const next = { ...prev };
      delete next[id];
      return next;
    });
  }

  if (!slug) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4 p-8 text-center">
        <MapPin className="w-10 h-10 text-muted-foreground" />
        <p className={`${type.body.m} text-muted-foreground max-w-sm`}>
          Build a site first, then come back here to add integrations.
        </p>
        <button onClick={onBack} className={`${interactions.chip} text-sm px-4 py-2 rounded-lg`}>
          ← Back to Design
        </button>
      </div>
    );
  }

  const enabledCount = Object.values(integrations).filter((r) => r?.enabled).length;

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="flex-shrink-0 px-6 pt-6 pb-4 border-b border-border">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className={`${interactions.chip} text-xs text-muted-foreground hover:text-foreground px-2 py-1 rounded-md`}
          >
            ← Design
          </button>
          <div className="flex-1" />
          {enabledCount > 0 && (
            <span className={`${type.eyebrow} text-primary`}>
              {enabledCount} active
            </span>
          )}
        </div>
        <h1 className={`${type.heading.l} text-foreground mt-3`}>Integrations</h1>
        <p className={`${type.body.s} text-muted-foreground mt-1`}>
          Add widgets to your site — no rebuild needed. Changes appear in the preview instantly.
        </p>
      </div>

      {/* Cards grid */}
      <div className="flex-1 overflow-y-auto p-6">
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <motion.div
            variants={safeMotion}
            initial="hidden"
            animate="visible"
            className="grid grid-cols-1 lg:grid-cols-2 gap-4"
          >
            {INTEGRATIONS.map((def) => (
              <IntegrationCard
                key={def.id}
                def={def}
                record={integrations[def.id]}
                onSave={handleSave}
                onRemove={handleRemove}
              />
            ))}
          </motion.div>
        )}

        {/* Footer note */}
        <p className={`${type.caption} text-center mt-8`}>
          Widgets appear in the preview immediately. They&apos;ll be included when you publish.
        </p>
      </div>
    </div>
  );
}
