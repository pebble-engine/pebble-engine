// Plain-Node verifier for safe-redirect.ts. Runs via:
//   node ui/v3/lib/safe-redirect.test.mjs
// Kept here so future-me can re-verify after refactors even without a JS
// test runner installed in v3.

// Inline copy of the function — duplicated so this script has no
// transpiler dep. Keep in sync with safe-redirect.ts.
function safeRedirect(raw, fallback = "/workspace") {
  if (typeof raw !== "string" || raw.length === 0) return fallback;
  if (raw.length < 2) return fallback;
  if (raw[0] !== "/") return fallback;
  if (raw[1] === "/" || raw[1] === "\\") return fallback;
  if (/[\x00-\x1f\x7f]/.test(raw)) return fallback;
  return raw;
}

const cases = [
  // [input, expected]
  ["/workspace",                    "/workspace"],
  ["/dashboard",                    "/dashboard"],
  ["/workspace#phase=plan",         "/workspace#phase=plan"],
  ["/workspace?next=foo",           "/workspace?next=foo"],
  ["https://evil.com",              "/workspace"],
  ["//evil.com",                    "/workspace"],
  ["/\\evil.com",                   "/workspace"],
  ["\\workspace",                   "/workspace"],
  ["",                              "/workspace"],
  [null,                            "/workspace"],
  [undefined,                       "/workspace"],
  ["javascript:alert(1)",           "/workspace"],
  ["/workspace\r\nSet-Cookie: x=y", "/workspace"],
  ["/",                             "/workspace"], // length<2 rejected
];

let fail = 0;
for (const [input, expected] of cases) {
  const got = safeRedirect(input);
  const ok = got === expected;
  if (!ok) fail++;
  console.log(
    (ok ? "PASS" : "FAIL") +
      "  in=" + JSON.stringify(input) +
      "  want=" + JSON.stringify(expected) +
      "  got=" + JSON.stringify(got),
  );
}
process.exit(fail === 0 ? 0 : 1);
