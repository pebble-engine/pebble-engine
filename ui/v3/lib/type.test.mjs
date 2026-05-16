// Plain-Node verifier for type.ts. Run via:
//   node ui/v3/lib/type.test.mjs
//
// Same pattern as motion.test.mjs — read source via fs.readFileSync and
// regex-check that the canonical structure is present. A bad edit to
// type.ts will surface here rather than silently passing against an
// inline copy.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SOURCE = readFileSync(resolve(__dirname, "type.ts"), "utf-8");

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

// ---- Module exports the `type` object as a const --------------------------
assertContains(
  SOURCE,
  /export const type\s*=\s*\{/,
  "exports `type` as a const",
);
assertContains(
  SOURCE,
  /\}\s*as const\s*;/,
  "type object is `as const` (literal types)",
);

// ---- Display roles --------------------------------------------------------
assertContains(SOURCE, /display\s*:\s*\{/, "display role group present");
for (const size of ["xl", "l", "m"]) {
  assertContains(
    SOURCE,
    new RegExp(`\\b${size}\\s*:\\s*"[^"]*font-display[^"]*"`, "m"),
    `display.${size} uses font-display family`,
  );
}

// ---- Heading roles --------------------------------------------------------
assertContains(SOURCE, /heading\s*:\s*\{/, "heading role group present");
for (const size of ["l", "m", "s"]) {
  // Heading roles must NOT use font-display (they use the default sans).
  const headingBlock = SOURCE.match(/heading\s*:\s*\{([\s\S]*?)\},/);
  if (!headingBlock) {
    failMsg(`could not isolate heading block for ${size} check`);
    continue;
  }
  const sizeMatch = new RegExp(`\\b${size}\\s*:\\s*"([^"]*)"`).exec(headingBlock[1]);
  if (!sizeMatch) {
    failMsg(`heading.${size} not found`);
    continue;
  }
  if (/font-display/.test(sizeMatch[1])) {
    failMsg(`heading.${size} should not use font-display (reserved for display.*)`);
  } else if (/font-semibold/.test(sizeMatch[1])) {
    pass(`heading.${size} present + uses font-semibold (no font-display)`);
  } else {
    failMsg(`heading.${size} should use font-semibold`);
  }
}

// ---- Body roles -----------------------------------------------------------
assertContains(SOURCE, /body\s*:\s*\{/, "body role group present");
for (const size of ["l", "m", "s"]) {
  const bodyBlock = SOURCE.match(/body\s*:\s*\{([\s\S]*?)\},/);
  if (!bodyBlock) {
    failMsg(`could not isolate body block for ${size} check`);
    continue;
  }
  if (new RegExp(`\\b${size}\\s*:\\s*"`).test(bodyBlock[1])) {
    pass(`body.${size} present`);
  } else {
    failMsg(`body.${size} missing`);
  }
}

// ---- Flat roles -----------------------------------------------------------
for (const role of ["label", "caption", "eyebrow", "mono"]) {
  assertContains(
    SOURCE,
    new RegExp(`\\b${role}\\s*:\\s*"[^"]+"`),
    `${role} role present (flat string)`,
  );
}

// ---- mono is the only role using font-mono --------------------------------
const monoBlock = SOURCE.match(/mono\s*:\s*"([^"]*)"/);
if (monoBlock && /font-mono/.test(monoBlock[1])) {
  pass("mono role uses font-mono family");
} else {
  failMsg("mono role missing font-mono family");
}

// ---- eyebrow uses arbitrary 11px size + uppercase + tracking --------------
const eyebrowBlock = SOURCE.match(/eyebrow\s*:\s*"([^"]*)"/);
if (eyebrowBlock) {
  const v = eyebrowBlock[1];
  const ok =
    /text-\[11px\]/.test(v) &&
    /uppercase/.test(v) &&
    /tracking-\[0\.08em\]/.test(v);
  if (ok) {
    pass("eyebrow uses text-[11px] + uppercase + tracking-[0.08em]");
  } else {
    failMsg("eyebrow missing required attributes (text-[11px], uppercase, tracking)");
  }
} else {
  failMsg("eyebrow role not found for attribute check");
}

process.exit(fail === 0 ? 0 : 1);
