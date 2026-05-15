/**
 * Reject any `?redirect=...` value that could bounce the browser to a
 * different origin after sign-in. The post-login flow in `app/login/
 * page.tsx` does `router.push(redirect)`, and Next.js' router will
 * happily do a full-page navigation if the href has an absolute scheme
 * or a protocol-relative authority — turning a legitimate Pebble login
 * link into an open-redirect into a phishing site.
 *
 * Accepts strictly: same-origin paths that start with `/<single slash>
 * <non-slash, non-backslash>`. Falls back to `/workspace` (the
 * standard post-auth landing) for anything else.
 *
 * Hand-traced cases — all expected to return `/workspace` unless noted:
 *   "/workspace"                      → "/workspace"            (OK)
 *   "/dashboard"                      → "/dashboard"            (OK)
 *   "/workspace#phase=plan"           → "/workspace#phase=plan" (OK — hash preserved)
 *   "/workspace?next=foo"             → "/workspace?next=foo"   (OK — query preserved)
 *   "https://evil.com"                → "/workspace"            (absolute URL rejected)
 *   "//evil.com"                      → "/workspace"            (protocol-relative rejected)
 *   "/\\evil.com"                     → "/workspace"            (backslash variant rejected)
 *   "\\workspace"                     → "/workspace"            (no leading slash rejected)
 *   ""                                → "/workspace"            (empty rejected)
 *   null / undefined                  → "/workspace"            (defensive)
 *   "javascript:alert(1)"             → "/workspace"            (no leading slash rejected)
 *   "/workspace\r\nSet-Cookie: x=y"   → "/workspace"            (CR/LF rejected)
 */
export function safeRedirect(
  raw: string | null | undefined,
  fallback: string = "/workspace",
): string {
  if (typeof raw !== "string" || raw.length === 0) return fallback;
  // Must start with a single forward slash, immediately followed by a
  // character that's neither another slash nor a backslash. That single
  // rule is enough to reject every authority-shifting form we know of:
  //   "//host"  — protocol-relative
  //   "/\\host" — backslash variant some browsers normalize to "//"
  //   "host"    — non-rooted; router would treat as same-origin under
  //               the current path which is OK but our policy is
  //               absolute paths only for predictability.
  if (raw.length < 2) return fallback;
  if (raw[0] !== "/") return fallback;
  if (raw[1] === "/" || raw[1] === "\\") return fallback;
  // CR/LF/TAB/etc. have no business in a router path — strip them out
  // by rejecting the whole value so we don't silently mutate intent.
  if (/[\x00-\x1f\x7f]/.test(raw)) return fallback;
  return raw;
}
