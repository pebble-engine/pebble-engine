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
  user_first_name?: string;       // captured at first session for personalized greeting
  design_reference_images?: Array<{ media_type: string; data: string; name?: string }>;
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

// localStorage so state survives tab close / browser restart.
// sessionStorage would lose everything on close, sending the user back
// to the welcome screen after a fresh tab open.
export function getBrief(): Brief {
  if (typeof window === "undefined") return {};
  try { return JSON.parse(localStorage.getItem(KEY_BRIEF) || "{}"); } catch { return {}; }
}
export function setBrief(b: Brief): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(KEY_BRIEF, JSON.stringify(b));
}
export function patchBrief(patch: Partial<Brief>): Brief {
  const next = { ...getBrief(), ...patch };
  setBrief(next);
  return next;
}
export function getPlan(): PebblePlan | null {
  if (typeof window === "undefined") return null;
  try { return JSON.parse(localStorage.getItem(KEY_PLAN) || "null"); } catch { return null; }
}
export function setPlan(p: PebblePlan): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(KEY_PLAN, JSON.stringify(p));
}
export function getLastBuild(): { slug: string; preview_url: string; [key: string]: unknown } | null {
  if (typeof window === "undefined") return null;
  try { return JSON.parse(localStorage.getItem(KEY_BUILD) || "null"); } catch { return null; }
}
export function setLastBuild(b: unknown): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(KEY_BUILD, JSON.stringify(b));
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
