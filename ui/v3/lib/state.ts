// Pebble state — sessionStorage-backed brief + plan + last build.
// Vanilla helpers so any screen can read/patch without importing a store.

export type Brief = Record<string, unknown> & {
  business_name?: string;
  business_type?: string;
  extra_context?: string;
  audience?: string[] | string;
  site_functions?: string[];
  brand_tone?: string;
  notes_freeform?: string;        // "anything the questions missed" — Plan-mode free-form input
  creative_direction?: string;    // free-text aesthetic hint, max 500 chars — keyword-classified into Layout DNA + injected as top-priority block in build prompt
  user_first_name?: string;       // captured at first session for personalized greeting
  design_reference_images?: Array<{ media_type: string; data: string; name?: string }>;
  /**
   * Phase 34 (2026-05-21) — build intent split.
   *
   * "business" (default, implicit when unset): real site for a real business.
   *   Conversion-optimized output, real Resend form, trust signals, schema.org.
   * "project": developer / designer sandbox or portfolio. Code reads cleanly,
   *   editorial layout latitude, understated CTAs, design fidelity over funnel.
   */
  intent?: "business" | "project";
  _industry_intel_key?: string;
  _design_dna_id?: string;
  _inspired_by?: string;       // set by /api/inspire: the source URL the user pasted
  _inspire_dna_hint?: string;  // set by /api/inspire: DNA card id we suggest. Consumed once by DnaPreview on /intake.
  _language?: string;          // BCP 47 code (en, es, fr, ja, ...); set by language picker, else server auto-detects
};

// Persistent, cross-session profile. Stored in localStorage so it survives
// browser restarts — sessionStorage is per-tab and would lose this.
const USER_PROFILE_KEY = "pebble.userProfile";

export type UserProfile = {
  firstName?: string;
};

export function getUserProfile(): UserProfile {
  if (typeof window === "undefined") return {};
  try { return JSON.parse(localStorage.getItem(USER_PROFILE_KEY) || "{}"); } catch { return {}; }
}

export function setUserProfile(p: UserProfile): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(USER_PROFILE_KEY, JSON.stringify(p));
}

export type PebblePage = {
  id: string;
  title: string;
  route: string;
  purpose: string;
  foundation: boolean;
};

export type PebbleFeature = { id: string; label: string; source: "brief" | "industry" | "universal" };

export type PebbleSetupItem = {
  id: string;
  label: string;
  status: "auto" | "pending" | "manual";
  dependencies: string[];
  notes: string;
};

export type PebblePlan = {
  schema_version: string;
  audience: string;
  goal: string;
  pages: PebblePage[];
  features: PebbleFeature[];
  style: {
    dna_id: string | null;
    label: string;
    mood: string;
    fonts: { display: string; body: string };
    palette: Record<string, string>;
  };
  setup_needs: PebbleSetupItem[];
  next_steps: string[];
  language?: {
    code:         string;     // BCP 47 primary (e.g. "es")
    english_name: string;     // "Spanish"
    native_name:  string;     // "Español"
    html_lang:    string;     // value used in <html lang="...">
  };
  meta: { business_name: string; industry_key: string | null; generated_at: string; engine_version: string };
};

const KEY_BRIEF = "pebble.brief";
const KEY_PLAN  = "pebble.plan";
const KEY_BUILD = "pebble.lastBuild";

// sessionStorage (tab-scoped) so two tabs editing two different projects
// don't clobber each other's brief / plan / lastBuild. NLM 2026-05-23
// critique #4: before this fix, opening project A in tab 1 and project B
// in tab 2 left BOTH tabs reading whichever project was most-recently
// loaded — a silent data-corruption bug now made worse by /workspace/<slug>
// URLs that explicitly invite multi-tab use.
//
// Trade-off: closing the tab mid-questionnaire loses the in-flight draft.
// Once a build exists, /workspace/<slug> rehydrates from the engine via
// fetchProjectState(), so the loss only affects pre-build drafts (~1% of
// sessions). userProfile stays in localStorage (cross-project preference).
//
// Migration story: returning users with stale `pebble.brief` etc. in
// localStorage will see those rows simply ignored. They land on welcome,
// not on a half-loaded prior project — that's the correct UX. We could
// add a one-shot copy-then-purge but it's not worth the code; the
// "lost state" is at most one incomplete questionnaire.
export function getBrief(): Brief {
  if (typeof window === "undefined") return {};
  try { return JSON.parse(sessionStorage.getItem(KEY_BRIEF) || "{}"); } catch { return {}; }
}
export function setBrief(b: Brief): void {
  if (typeof window === "undefined") return;
  sessionStorage.setItem(KEY_BRIEF, JSON.stringify(b));
}
export function patchBrief(patch: Partial<Brief>): Brief {
  const next = { ...getBrief(), ...patch };
  setBrief(next);
  return next;
}
export function getPlan(): PebblePlan | null {
  if (typeof window === "undefined") return null;
  try { return JSON.parse(sessionStorage.getItem(KEY_PLAN) || "null"); } catch { return null; }
}
export function setPlan(p: PebblePlan): void {
  if (typeof window === "undefined") return;
  sessionStorage.setItem(KEY_PLAN, JSON.stringify(p));
}
export function getLastBuild(): { slug: string; preview_url: string; [key: string]: unknown } | null {
  if (typeof window === "undefined") return null;
  try { return JSON.parse(sessionStorage.getItem(KEY_BUILD) || "null"); } catch { return null; }
}
export function setLastBuild(b: unknown): void {
  if (typeof window === "undefined") return;
  sessionStorage.setItem(KEY_BUILD, JSON.stringify(b));
}

/**
 * Wipe the in-progress brief + plan + last-build pointer so the next
 * /workspace visit gets a clean canvas. Use when the user clicks
 * "Start a new project" — the questionnaire then opens blank.
 *
 * Does NOT touch userProfile or other cross-project preferences.
 *
 * 2026-05-20 Phase 15a: added because Marc's 4th rebuild kept landing
 * on the same "Untitled Project" with prior chips pre-selected. UX gap.
 *
 * 2026-05-23: storage backend swapped to sessionStorage (see KEY_*
 * comment block) so the removes target the right place. Also purges
 * the legacy localStorage keys for users who still have stale rows
 * from the old code — one-shot housekeeping, runs every time which is
 * cheap.
 */
export function clearBriefForNewProject(): void {
  if (typeof window === "undefined") return;
  sessionStorage.removeItem(KEY_BRIEF);
  sessionStorage.removeItem(KEY_PLAN);
  sessionStorage.removeItem(KEY_BUILD);
  // Also clean up any leftover localStorage rows from before the
  // sessionStorage migration. Safe no-op when keys are absent.
  localStorage.removeItem(KEY_BRIEF);
  localStorage.removeItem(KEY_PLAN);
  localStorage.removeItem(KEY_BUILD);
}

/**
 * Best-effort derivation of a project name from the user's idea text.
 * Returns the first sentence (capped at 60 chars) so the user sees a
 * recognisable name in the workspace top nav AND the build's output dir
 * gets a useful slug (instead of "untitled-project").
 *
 * Phase 20a (2026-05-20): split obvious camelCase autocorrect mashing
 * ("inQueens" → "in Queens"), then title-case words that have no
 * uppercase letter yet (preserves "iPhone", "ACME", "McDonald"). The
 * engine repeats the same sanitization server-side as the source of
 * truth (see pebble/text.py) — this one only exists for the top-nav
 * display so the user sees the corrected name as they type.
 *
 * The user can still edit the name in the top nav after the fact.
 */
export function deriveProjectName(ideaText: string): string {
  if (!ideaText) return "New project";
  // First sentence break
  const firstSentence = ideaText
    .replace(/\s+/g, " ")
    .trim()
    .split(/[.!?]/)[0]
    .trim();
  // Cap at 60 chars so the slug doesn't get absurd
  const capped = firstSentence.length > 60
    ? firstSentence.slice(0, 60).trim() + "…"
    : firstSentence;
  if (!capped) return "New project";
  // Split camelCase runs where 2+ lowercase chars meet uppercase
  // (preserves brand casing like iPhone/iPad — single-char prefix is safe).
  const split = capped.replace(/([a-z]{2,})([A-Z])/g, "$1 $2");
  // Title-case word-by-word, leaving words that already contain uppercase.
  return split
    .split(" ")
    .map((w) => {
      if (!w) return w;
      if (/[A-Z]/.test(w)) return w; // ACME, iPhone, McDonald — preserve
      return w[0].toUpperCase() + w.slice(1);
    })
    .join(" ");
}

// Industry heuristic — quick keyword match used by intake.
// The engine's industry resolver does the real work via fuzzy match +
// LLM fallback; this just picks a plausible starting guess.
const INDUSTRY_HINTS: Array<[string, string]> = [
  ["bakery", "bakery"], ["restaurant", "restaurant"], ["coffee", "cafe"], ["cafe", "cafe"],
  ["dentist", "dentist"], ["yoga", "yoga_studio"], ["plumb", "plumbing"], ["hvac", "hvac"],
  ["lawyer", "law_firm"], ["attorney", "law_firm"], ["real estate", "real_estate"],
  ["photo", "photography"], ["therapist", "therapist"], ["salon", "hair_salon"],
  ["barber", "barbershop"], ["spa", "spa"], ["fitness", "gym"], ["gym", "gym"],
  ["pet", "pet_grooming"], ["clean", "cleaning_service"], ["landscap", "landscaping"],
  ["construct", "construction"], ["consult", "consultant"], ["agency", "agency"],
  ["jewel", "jeweler"], ["car", "auto_repair"], ["auto", "auto_repair"],
];

export function guessIndustryFromIdea(idea: string): string {
  const lower = idea.toLowerCase();
  for (const [needle, key] of INDUSTRY_HINTS) {
    if (lower.includes(needle)) return key;
  }
  return "small_business";
}
