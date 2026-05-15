// Plain-Node verifier for motion.ts. Run via:
//   node ui/v3/lib/motion.test.mjs
//
// We can't import the .ts file without transpilation, so this script
// reads motion.ts via fs.readFileSync and regex-checks that the canonical
// values are present in the actual source. A bad edit to motion.ts will
// surface as a FAIL here rather than silently passing against an inline copy.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SOURCE = readFileSync(resolve(__dirname, "motion.ts"), "utf-8");

let fail = 0;

function pass(msg) { console.log("PASS  " + msg); }
function failMsg(msg) { console.log("FAIL  " + msg); fail++; }

function assertContains(source, pattern, label) {
  if (pattern.test(source)) {
    pass(label);
  } else {
    failMsg(label);
  }
}

// ---- Duration constants (exact numeric values in source) --------------------
assertContains(SOURCE, /export const MICRO\s*=\s*120\b/, "MICRO = 120 present in source");
assertContains(SOURCE, /export const SHORT\s*=\s*200\b/, "SHORT = 200 present in source");
assertContains(SOURCE, /export const STANDARD\s*=\s*480\b/, "STANDARD = 480 present in source");
assertContains(SOURCE, /export const SLOW\s*=\s*700\b/, "SLOW = 700 present in source");

// ---- Easing tuples ----------------------------------------------------------
assertContains(
  SOURCE,
  /export const EASE_CINEMATIC[^=]*=\s*\[0\.22,\s*1,\s*0\.36,\s*1\]/,
  "EASE_CINEMATIC = [0.22, 1, 0.36, 1] present in source"
);
assertContains(
  SOURCE,
  /export const EASE_QUIET[^=]*=\s*\[0\.4,\s*0,\s*0\.2,\s*1\]/,
  "EASE_QUIET = [0.4, 0, 0.2, 1] present in source"
);

// ---- Variant exports --------------------------------------------------------
const EXPECTED_VARIANTS = [
  "fadeUp", "phaseEnter", "phaseExit",
  "railStep", "chipDeck", "cardHover", "dropletPulse",
];

// Uniqueness check (structural)
const uniqueNames = new Set(EXPECTED_VARIANTS);
if (uniqueNames.size === EXPECTED_VARIANTS.length) {
  pass(`variant names list (${EXPECTED_VARIANTS.length}) is unique`);
} else {
  failMsg("variant names list has duplicates");
}

// Each variant must appear as an `export const NAME` declaration in source
for (const name of EXPECTED_VARIANTS) {
  assertContains(
    SOURCE,
    new RegExp(`export const ${name}\\s*:`),
    `export const ${name} declared in source`
  );
}

// ---- Duration ordering (structural, derived from source values) -------------
// Parse the four values out of source to confirm ordering still holds.
const durationMatches = {
  MICRO:    SOURCE.match(/export const MICRO\s*=\s*(\d+)/),
  SHORT:    SOURCE.match(/export const SHORT\s*=\s*(\d+)/),
  STANDARD: SOURCE.match(/export const STANDARD\s*=\s*(\d+)/),
  SLOW:     SOURCE.match(/export const SLOW\s*=\s*(\d+)/),
};
const allMatched = Object.values(durationMatches).every(Boolean);
if (allMatched) {
  const [micro, short, standard, slow] = [
    durationMatches.MICRO, durationMatches.SHORT,
    durationMatches.STANDARD, durationMatches.SLOW,
  ].map((m) => Number(m[1]));
  if (micro < short && short < standard && standard < slow) {
    pass("durations are ordered MICRO < SHORT < STANDARD < SLOW in source");
  } else {
    failMsg("durations are not ordered correctly in source");
  }
} else {
  failMsg("could not parse all duration values from source for ordering check");
}

// ---- Helper functions are exported ------------------------------------------
assertContains(SOURCE, /export function prefersReducedMotion/, "prefersReducedMotion exported");
assertContains(SOURCE, /export function withReducedMotion/, "withReducedMotion exported");

process.exit(fail === 0 ? 0 : 1);
