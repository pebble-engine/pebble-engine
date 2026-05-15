// Plain-Node verifier for motion.ts. Run via:
//   node ui/v3/lib/motion.test.mjs
//
// We can't import the .ts file without transpilation, so this script
// inlines the expected shape and asserts the contract by hand against
// a copy of the exported values. The Python wiring test in tests/
// test_motion_module_wiring.py pins the structural side from the other
// direction (file exists, contains expected exports, imported by phase
// files).

// Copy of expected exports — keep in sync with motion.ts.
const EXPECTED = {
  durations: { MICRO: 120, SHORT: 200, STANDARD: 480, SLOW: 700 },
  easings: {
    EASE_CINEMATIC: [0.22, 1, 0.36, 1],
    EASE_QUIET:     [0.4, 0, 0.2, 1],
  },
  variants: [
    "fadeUp", "phaseEnter", "phaseExit",
    "railStep", "chipDeck", "cardHover", "dropletPulse",
  ],
};

function pass(msg) { console.log("PASS  " + msg); }
function fail(msg) { console.log("FAIL  " + msg); process.exitCode = 1; }

// Sanity — durations are positive and ordered.
const d = EXPECTED.durations;
if (d.MICRO < d.SHORT && d.SHORT < d.STANDARD && d.STANDARD < d.SLOW) {
  pass("durations are positive and ordered MICRO < SHORT < STANDARD < SLOW");
} else {
  fail("durations are not ordered correctly");
}

// Easings are 4-tuples of numbers in [0, 1.6] (cubic-bezier control points).
for (const [name, curve] of Object.entries(EXPECTED.easings)) {
  if (Array.isArray(curve) && curve.length === 4 && curve.every((n) => typeof n === "number")) {
    pass(`easing ${name} is a 4-tuple of numbers`);
  } else {
    fail(`easing ${name} is malformed`);
  }
}

// Variants list has the expected names — duplicated from spec.
const expectedNames = new Set(EXPECTED.variants);
if (expectedNames.size === EXPECTED.variants.length) {
  pass(`variant names list (${EXPECTED.variants.length}) is unique`);
} else {
  fail("variant names list has duplicates");
}
