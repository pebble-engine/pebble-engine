// Plain-Node verifier for pickPreviewUrl from lib/api.ts. Runs via:
//   node ui/v3/lib/pick-preview-url.test.mjs
//
// Background: generated sites are Next.js apps. The static `/preview/<slug>/`
// path 404s for them because there's no compiled `index.html` on disk —
// `next dev` renders pages live on a free port. When `PEBBLE_AUTO_RUN=true`
// the engine returns `dev_server.url` pointing at that live process; the
// iframe should prefer it. The helper falls back to the static preview path
// when no live server is available (engine restart, dashboard-resume of an
// older project, etc.) and to "about:blank" if no URL information at all.

// Inline copy of the function — duplicated so this script has no
// transpiler dep. Keep in sync with lib/api.ts:pickPreviewUrl.
function pickPreviewUrl(build) {
  const devUrl = build?.dev_server?.url;
  if (typeof devUrl === "string" && devUrl.length > 0) return devUrl;
  if (build?.preview_url) return build.preview_url;
  return "about:blank";
}

const cases = [
  // [name, input, expected]
  ["null build",
    null,
    "about:blank"],
  ["undefined build",
    undefined,
    "about:blank"],
  ["empty object",
    {},
    "about:blank"],
  ["only preview_url",
    { preview_url: "/preview/foo/" },
    "/preview/foo/"],
  ["dev_server.url present, no preview_url",
    { dev_server: { url: "http://127.0.0.1:51964" } },
    "http://127.0.0.1:51964"],
  ["both present — dev_server wins",
    { preview_url: "/preview/foo/", dev_server: { url: "http://127.0.0.1:51964" } },
    "http://127.0.0.1:51964"],
  ["dev_server.url empty string falls back",
    { preview_url: "/preview/foo/", dev_server: { url: "" } },
    "/preview/foo/"],
  ["dev_server.url null falls back",
    { preview_url: "/preview/foo/", dev_server: { url: null } },
    "/preview/foo/"],
  ["dev_server present but url missing",
    { preview_url: "/preview/foo/", dev_server: { enabled: true, port: null } },
    "/preview/foo/"],
  ["dev_server.url number-ish falls back (defensive)",
    { preview_url: "/preview/foo/", dev_server: { url: 8000 } },
    "/preview/foo/"],
  ["only dev_server, no url field at all",
    { dev_server: { enabled: false, errors: ["auto-run disabled"] } },
    "about:blank"],
];

let fail = 0;
for (const [name, input, expected] of cases) {
  const got = pickPreviewUrl(input);
  const ok = got === expected;
  if (!ok) fail++;
  console.log(
    `${ok ? "✓" : "✗"} ${name.padEnd(50)} → ${JSON.stringify(got)}` +
    (ok ? "" : ` (expected ${JSON.stringify(expected)})`),
  );
}

if (fail > 0) {
  console.log(`\n${fail} case(s) failed`);
  process.exit(1);
}
console.log(`\nAll ${cases.length} cases passed`);
