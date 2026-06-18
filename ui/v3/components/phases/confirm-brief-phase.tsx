"use client";

import { useEffect, useMemo, useState } from "react";
import { motion, MotionConfig } from "framer-motion";
import { ArrowRight, Pencil } from "lucide-react";
import { fetchBriefInfer } from "@/lib/api";
import { formatProjectTitle, industryLabel } from "@/lib/brief-display";
import { getBrief, patchBrief } from "@/lib/state";
import { STANDARD_S, EASE_CINEMATIC } from "@/lib/motion";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";

const FUNCTION_LABELS: Record<string, string> = {
  presence: "See your story",
  leads: "Get in touch",
  booking: "Book online",
  ecommerce: "Buy something",
  portfolio: "See your work",
  payment: "Pay or donate",
};
const GOAL_CHIPS = [
  { id: "leads", label: "Get contacted" },
  { id: "booking", label: "Take bookings" },
  { id: "presence", label: "Tell our story" },
  { id: "ecommerce", label: "Sell online" },
] as const;

type Props = {
  onConfirm: () => void;
  planRequired: boolean;
};

export function ConfirmBriefPhase({ onConfirm, planRequired }: Props) {
  const brief = getBrief();
  const rawPrompt = (brief._raw_prompt as string) || (brief.extra_context as string) || "";

  const [name, setName] = useState((brief.business_name as string) || "");
  const [location, setLocation] = useState((brief.location as string) || "");
  const [businessType, setBusinessType] = useState((brief.business_type as string) || "");
  const [goal, setGoal] = useState<string>(
    ((brief.site_functions as string[]) || ["leads"])[0] || "leads",
  );
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);

  const skipInfer = Boolean(
    brief._inspired_by || brief._extracted_logo_url || brief._extracted_hero_copy,
  );

  const preview = useMemo(
    () =>
      formatProjectTitle({
        business_name: name,
        business_type: businessType,
        location,
        _raw_prompt: rawPrompt,
      }),
    [name, businessType, location, rawPrompt],
  );

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      if (skipInfer) {
        if (brief.business_name) setName(brief.business_name as string);
        if (brief.location) setLocation(brief.location as string);
        if (brief.business_type) setBusinessType(brief.business_type as string);
        const funcs = brief.site_functions as string[] | undefined;
        if (funcs?.[0]) setGoal(funcs[0]);
        setLoading(false);
        return;
      }
      if (!rawPrompt.trim()) {
        setLoading(false);
        return;
      }
      try {
        const inferred = await fetchBriefInfer(rawPrompt, (brief.intent as string) || "business");
        if (cancelled || !inferred.ok) return;
        const shortName = inferred.display_name || inferred.business_name;
        if (shortName) setName(shortName);
        if (!brief.location && inferred.location) setLocation(inferred.location);
        if (!brief.business_type && inferred.business_type) setBusinessType(inferred.business_type);
        if (inferred.site_functions?.[0]) setGoal(inferred.site_functions[0]);
        patchBrief({
          business_name: shortName,
          business_type: inferred.business_type,
          location: inferred.location || undefined,
          audience: inferred.audience,
          site_functions: inferred.site_functions,
          brand_tone: inferred.brand_tone,
          _raw_prompt: rawPrompt,
        });
      } catch {
        /* graceful — user can still edit manually */
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleConfirm() {
    const funcs = [goal];
    if (goal !== "presence" && !funcs.includes("presence")) funcs.push("presence");
    patchBrief({
      business_name: name.trim() || industryLabel(businessType) || "New project",
      business_type: businessType.trim() || "small_business",
      location: location.trim() || undefined,
      site_functions: funcs,
      _raw_prompt: rawPrompt,
      planFirst: planRequired ? true : brief.planFirst,
    });
    onConfirm();
  }

  return (
    <MotionConfig reducedMotion="user">
      <div className="flex flex-col h-full min-h-[60vh]">
        <main className="flex-grow flex flex-col items-center justify-center px-4 md:px-8 py-8 pb-safe">
          <div className="max-w-xl w-full space-y-8">
            <div className="text-center space-y-2">
              <h1 className={`${type.readable.title} text-center`}>Here&apos;s what we heard</h1>
              <p className={`${type.readable.body} text-muted-foreground`}>
                Sound right? You can change anything before we start.
              </p>
            </div>

            {loading ? (
              <p className={`${type.readable.body} text-center text-muted-foreground`}>One moment…</p>
            ) : (
              <div className="rounded-2xl bg-card border border-border p-6 space-y-6 shadow-[var(--shadow-1)]">
                {!editing ? (
                  <>
                    <div className="break-words">
                      <p className={`${type.readable.label} mb-1`}>Your business</p>
                      <p className={`${type.readable.title} break-words`}>
                        {preview.headline || "Your business"}
                      </p>
                      {preview.subline && (
                        <p className={`${type.readable.body} text-muted-foreground mt-1 capitalize`}>
                          {preview.subline}
                        </p>
                      )}
                    </div>
                    {location && (
                      <div>
                        <p className={`${type.readable.label} mb-1`}>Area</p>
                        <p className={`${type.readable.body} text-foreground`}>{location}</p>
                      </div>
                    )}
                    <div>
                      <p className={`${type.readable.label} mb-1`}>Main goal</p>
                      <p className={`${type.readable.body} text-foreground`}>
                        {FUNCTION_LABELS[goal] ?? goal}
                      </p>
                    </div>
                  </>
                ) : (
                  <div className="space-y-4">
                    <label className="block space-y-2">
                      <span className={type.readable.label}>Business name</span>
                      <input
                        className={`w-full rounded-lg border border-border bg-background px-4 py-3 ${type.readable.body}`}
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                      />
                    </label>
                    <label className="block space-y-2">
                      <span className={type.readable.label}>Location</span>
                      <input
                        className={`w-full rounded-lg border border-border bg-background px-4 py-3 ${type.readable.body}`}
                        placeholder="City or neighborhood"
                        value={location}
                        onChange={(e) => setLocation(e.target.value)}
                      />
                    </label>
                    <div className="block space-y-2">
                      <span className={type.readable.label}>What should visitors do?</span>
                      <div className="flex flex-wrap gap-2 pt-1">
                        {GOAL_CHIPS.map((c) => (
                          <button
                            key={c.id}
                            type="button"
                            onClick={() => setGoal(c.id)}
                            className={`${type.readable.chip} rounded-full border transition-colors ${
                              goal === c.id
                                ? "bg-primary text-primary-foreground border-primary"
                                : "border-border hover:border-foreground/40"
                            }`}
                          >
                            {c.label}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            <div className="flex flex-col gap-3 pb-safe">
              <motion.button
                whileTap={{ scale: 0.97 }}
                disabled={loading}
                onClick={handleConfirm}
                className={`${interactions.button} ${type.readable.cta} w-full flex items-center justify-center gap-2 bg-primary text-primary-foreground px-8 rounded-lg shadow-md font-semibold disabled:opacity-50`}
              >
                Yes, let&apos;s go <ArrowRight className="w-5 h-5" />
              </motion.button>
              {!editing ? (
                <button
                  type="button"
                  onClick={() => setEditing(true)}
                  className={`${interactions.chip} w-full flex items-center justify-center gap-2 text-muted-foreground hover:text-foreground min-h-11 ${type.readable.body}`}
                >
                  <Pencil className="w-4 h-4" aria-hidden />
                  Change anything
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => setEditing(false)}
                  className={`${type.readable.body} text-muted-foreground hover:text-foreground text-center min-h-11`}
                >
                  Done editing
                </button>
              )}
            </div>
          </div>
        </main>
      </div>
    </MotionConfig>
  );
}
