// Plain-Node verifier for interactions.ts. Run via:
//   node ui/v3/lib/interactions.test.mjs
//
// Same pattern as type.test.mjs — read source via fs.readFileSync and
// regex-check that the canonical structure is present. A bad edit to
// interactions.ts will surface here rather than silently passing against an
// inline copy.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SOURCE = readFileSync(resolve(__dirname, "interactions.ts"), "utf-8");

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

// ---- Module exports the `interactions` object as a const -----------------
assertContains(
  SOURCE,
  /export\s+const\s+interactions\s*=\s*\{/,
  "exports `interactions` as a const",
);
assertContains(
  SOURCE,
  /\}\s*as const\s*;/,
  "interactions object is `as const` (literal types)",
);

// ---- All six role keys present -----------------------------------------------
const roles = ["button", "chip", "card", "iconButton", "link", "focusRing"];
for (const role of roles) {
  assertContains(
    SOURCE,
    new RegExp(`\\b${role}\\s*:`),
    `${role} role present`,
  );
}

// ---- button role critical classes ------------------------------------------
assertContains(
  SOURCE,
  /button\s*:[\s\S]*?transition-all/,
  "button contains transition-all",
);
assertContains(
  SOURCE,
  /button\s*:[\s\S]*?hover:opacity-90/,
  "button contains hover:opacity-90",
);
assertContains(
  SOURCE,
  /button\s*:[\s\S]*?active:scale-\[0\.98\]/,
  "button contains active:scale-[0.98]",
);
assertContains(
  SOURCE,
  /button\s*:[\s\S]*?focus-visible:ring-2/,
  "button contains focus-visible:ring-2",
);
assertContains(
  SOURCE,
  /button\s*:[\s\S]*?motion-reduce:transition-none/,
  "button contains motion-reduce:transition-none",
);

// ---- chip role critical classes -------------------------------------------
assertContains(
  SOURCE,
  /chip\s*:[\s\S]*?transition-colors/,
  "chip contains transition-colors",
);
assertContains(
  SOURCE,
  /chip\s*:[\s\S]*?hover:bg-accent/,
  "chip contains hover:bg-accent",
);
assertContains(
  SOURCE,
  /chip\s*:[\s\S]*?focus-visible:ring-2/,
  "chip contains focus-visible:ring-2",
);

// ---- card role critical classes -------------------------------------------
assertContains(
  SOURCE,
  /card\s*:[\s\S]*?transition-all/,
  "card contains transition-all",
);
assertContains(
  SOURCE,
  /card\s*:[\s\S]*?hover:-translate-y-0\.5/,
  "card contains hover:-translate-y-0.5",
);
assertContains(
  SOURCE,
  /card\s*:[\s\S]*?hover:shadow-md/,
  "card contains hover:shadow-md",
);
assertContains(
  SOURCE,
  /card\s*:[\s\S]*?motion-reduce:hover:translate-y-0/,
  "card contains motion-reduce:hover:translate-y-0",
);

// ---- iconButton role critical classes -----------------------------------
assertContains(
  SOURCE,
  /iconButton\s*:[\s\S]*?hover:bg-accent/,
  "iconButton contains hover:bg-accent",
);
assertContains(
  SOURCE,
  /iconButton\s*:[\s\S]*?active:scale-95/,
  "iconButton contains active:scale-95",
);
assertContains(
  SOURCE,
  /iconButton\s*:[\s\S]*?motion-reduce:active:scale-100/,
  "iconButton contains motion-reduce:active:scale-100",
);

// ---- link role critical classes -------------------------------------------
assertContains(
  SOURCE,
  /link\s*:[\s\S]*?transition-colors/,
  "link contains transition-colors",
);
assertContains(
  SOURCE,
  /link\s*:[\s\S]*?hover:text-foreground/,
  "link contains hover:text-foreground",
);

// ---- focusRing role critical classes -----------------------------------
assertContains(
  SOURCE,
  /focusRing\s*:\s*"[^"]*ring-2[^"]*"/,
  "focusRing contains ring-2",
);
assertContains(
  SOURCE,
  /focusRing\s*:\s*"[^"]*ring-offset-2[^"]*"/,
  "focusRing contains ring-offset-2",
);

process.exit(fail === 0 ? 0 : 1);
