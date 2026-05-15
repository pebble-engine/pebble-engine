import { type NextRequest } from "next/server";
import { updateSession } from "@/lib/supabase/middleware";

/**
 * Next.js 16 "proxy" (formerly "middleware"). Runs on every request
 * before the route handler. Delegates to the Supabase session refresher,
 * which also enforces route protection for /workspace and /dashboard.
 *
 * Renamed from middleware.ts because Next.js 16 deprecated the
 * `middleware` convention in favour of `proxy`.
 */
export async function proxy(request: NextRequest) {
  return await updateSession(request);
}

export const config = {
  matcher: [
    // Run on every request EXCEPT static assets and image optimisations —
    // both are bandwidth-sensitive and don't need auth refresh.
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico)$).*)",
  ],
};
