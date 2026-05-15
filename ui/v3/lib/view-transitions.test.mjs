// Plain-Node verifier for view-transitions.ts. Run via:
//   node ui/v3/lib/view-transitions.test.mjs
//
// Reads the actual source file via fs.readFileSync (same pattern as
// motion.test.mjs after its fix) so the verifier has teeth — a
// destructive edit to view-transitions.ts will produce a FAIL.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SOURCE = readFileSync(resolve(__dirname, "view-transitions.ts"), "utf-8");

let fail = 0;
function pass(msg) { console.log("PASS  " + msg); }
function fails(msg) { console.log("FAIL  " + msg); fail++; }

// Capability check export exists with a typeof document undefined guard.
if (/export\s+function\s+supportsViewTransitions\s*\(\s*\)\s*:\s*boolean/.test(SOURCE)) {
  pass("supportsViewTransitions exported with boolean return type");
} else {
  fails("supportsViewTransitions missing or wrong signature");
}

if (/typeof\s+document\s*===\s*['\"]undefined['\"]/.test(SOURCE)) {
  pass("supportsViewTransitions guards against server-side document access");
} else {
  fails("server-side guard for document missing");
}

// safeStartViewTransition wrapper.
if (/export\s+function\s+safeStartViewTransition\s*\(\s*callback\s*:\s*\(\s*\)\s*=>\s*void\s*\)\s*:\s*void/.test(SOURCE)) {
  pass("safeStartViewTransition exported with correct signature");
} else {
  fails("safeStartViewTransition missing or wrong signature");
}

// Fallback branch invokes callback() synchronously.
if (/else\s*\{\s*callback\(\);?\s*\}/.test(SOURCE)) {
  pass("fallback branch invokes callback() synchronously");
} else {
  fails("synchronous-fallback else branch missing");
}

// Runtime test of the function logic, inlined since we can't import .ts.
function supportsViewTransitions() {
  return typeof document !== "undefined"
    && typeof document.startViewTransition === "function";
}

function safeStartViewTransition(callback) {
  if (supportsViewTransitions()) {
    document.startViewTransition(callback);
  } else {
    callback();
  }
}

if (supportsViewTransitions() === false) {
  pass("supportsViewTransitions returns false in Node (no document)");
} else {
  fails("supportsViewTransitions did not return false in Node");
}

let called = false;
safeStartViewTransition(() => { called = true; });
if (called) {
  pass("safeStartViewTransition invokes callback synchronously when unsupported");
} else {
  fails("callback was not invoked when View Transitions unsupported");
}

process.exit(fail === 0 ? 0 : 1);
