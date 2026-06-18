/**
 * Short project titles for confirm/plan UI — mirrors pebble/brief_display.py.
 */

export type BriefLike = {
  business_name?: string;
  business_type?: string;
  location?: string;
  _raw_prompt?: string;
  extra_context?: string;
};

const MAX_WORDS = 4;
const MAX_CHARS = 40;

const META_MARKERS = [
  "build a website",
  "build a site",
  "need a website",
  "website for my",
  "site for my",
  "it's called",
  "its called",
];

function capWords(text: string): string {
  const cleaned = text.trim().replace(/\s+/g, " ");
  if (!cleaned) return "";
  let words = cleaned.split(" ");
  if (words.length > MAX_WORDS) words = words.slice(0, MAX_WORDS);
  let out = words.join(" ");
  if (out.length > MAX_CHARS) {
    out = out.slice(0, MAX_CHARS).replace(/\s+\S*$/, "").trim();
  }
  return out;
}

export function industryLabel(industryKey?: string): string {
  const key = (industryKey || "").trim().replace(/-/g, "_");
  if (!key || key === "small_business") return "Business";
  return key
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(" ");
}

export function looksLikeMetaName(name: string): boolean {
  const lower = name.toLowerCase().trim();
  if (!lower || lower.length > MAX_CHARS) return true;
  if (META_MARKERS.some((m) => lower.includes(m))) return true;
  if (/^my\s+\w+\s+business$/.test(lower)) return true;
  if (lower.endsWith(" business") && lower.split(/\s+/).length <= 4) return true;
  return false;
}

export function extractBusinessName(rawPrompt: string): string {
  const raw = rawPrompt.trim();
  if (!raw) return "";

  const calledQuoted = raw.match(/(?:called|named)\s+["']([^"']{2,60})["']/i);
  if (calledQuoted?.[1]) {
    const c = capWords(calledQuoted[1]);
    if (c && !looksLikeMetaName(c)) return c;
  }

  const itsCalled = raw.match(
    /(?:it'?s|its|is)\s+called\s+([A-Za-z0-9][\w\s&'.-]{1,58}?)(?:\s*[,.\-–—]|$)/i,
  );
  if (itsCalled?.[1]) {
    const c = capWords(itsCalled[1]);
    if (c && !looksLikeMetaName(c)) return c;
  }

  let stripped = raw.split(/[.!?]/)[0].trim();
  stripped = stripped
    .replace(
      /^(?:build\s+(?:a|me|us)?\s*(?:website|site|web\s*site|page)\s+(?:for\s+)?)/i,
      "",
    )
    .replace(/^(?:i\s+)?need\s+(?:a|an)\s+(?:website|site)\s+(?:for\s+)?/i, "")
    .replace(/^i\s+(?:own|run|have|started)\s+(?:a|an|the)\s+/i, "")
    .trim();

  if (/^my\s+\w+\s+business$/i.test(stripped)) return "";

  const locMatch = stripped.match(
    /^(?:(?:a|an|the)\s+)?(\w+)\s+in\s+([A-Z][a-zA-Z\s.'-]{1,40})$/i,
  );
  if (locMatch) {
    const c = capWords(`${locMatch[2]} ${locMatch[1]}`);
    if (c) return c;
  }

  const candidate = capWords(stripped);
  if (candidate && !looksLikeMetaName(candidate)) return candidate;
  return "";
}

export function displayName(brief: BriefLike): string {
  const raw = (brief._raw_prompt || brief.extra_context || "").trim();
  const name = (brief.business_name || "").trim();
  const btype = brief.business_type || "";

  if (name && !looksLikeMetaName(name)) return capWords(name) || industryLabel(btype);

  const extracted = raw ? extractBusinessName(raw) : "";
  if (extracted) return extracted;

  if (name) {
    const short = capWords(name);
    if (short && !looksLikeMetaName(short)) return short;
  }

  return industryLabel(btype);
}

export function formatProjectTitle(brief: BriefLike): { headline: string; subline: string } {
  const headline = displayName(brief);
  const industry = industryLabel(brief.business_type);
  const loc = (brief.location || "").trim();
  const parts = [industry !== headline ? industry : "", loc].filter(Boolean);
  return { headline, subline: parts.join(" · ") };
}
