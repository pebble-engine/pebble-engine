// Pebble-flavored readable subdomain generator.
//
// Inspired by the auto-generated "<adj>-<noun>-<verb>.lovable.app" pattern
// without reusing their word lists. Ours lean editorial + tactile to match
// the brand voice (stone, paper, brass, etc.).
//
// Deterministic if you pass a seed (the project slug works as one) — that
// way the same project gets the same hostname every time the user opens it.

const ADJECTIVES = [
  "calm", "warm", "wide", "soft", "slow", "bright", "still", "quiet",
  "honest", "plain", "true", "kind", "open", "ready", "fresh", "even",
  "clear", "patient", "careful", "tender", "humble", "steady",
];

const NOUNS = [
  "stone", "river", "willow", "kettle", "paper", "brass", "linen", "ember",
  "harbor", "meadow", "garden", "studio", "atelier", "porch", "alcove",
  "library", "pavilion", "lantern", "veranda", "orchard",
];

const VERBS = [
  "rests", "breathes", "lingers", "carries", "settles", "remembers",
  "ripens", "gathers", "anchors", "opens", "holds", "shines", "weighs",
  "waits", "tends", "marks", "guides",
];

function hashString(s: string): number {
  // Tiny deterministic hash — djb2 variant. Not cryptographic; we just want
  // a stable index into the word lists for a given input.
  let h = 5381;
  for (let i = 0; i < s.length; i++) {
    h = (h * 33) ^ s.charCodeAt(i);
  }
  return h >>> 0;
}

function pick<T>(list: T[], seed: number, offset: number): T {
  return list[(seed + offset) % list.length];
}

/**
 * Generate a readable three-word subdomain.
 *
 * @param seed Optional stable input — passing the project slug here means
 *             the same project always gets the same subdomain.
 */
export function generateSubdomain(seed?: string): string {
  const base = seed ? hashString(seed) : Math.floor(Math.random() * 1_000_000);
  const adj  = pick(ADJECTIVES, base, 0);
  const noun = pick(NOUNS,      base, 7);
  const verb = pick(VERBS,      base, 13);
  return `${adj}-${noun}-${verb}`;
}
