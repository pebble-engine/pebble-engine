// Thin client for the Pebble engine.
//
// Important architecture note: long-running endpoints like /api/generate
// take 90–180s. Next.js' dev-server rewrite proxy (Turbopack) closes the
// connection well before that with a "socket hang up" ECONNRESET, which
// fires a client-side fetch rejection EVEN THOUGH the engine successfully
// completed the build and wrote files to disk. The user then sees "build
// failed," retries, gets billed twice, and asks for a refund.
//
// Fix: when NEXT_PUBLIC_PEBBLE_ENGINE_URL is set, the client calls the
// engine directly via CORS (engine already sends Access-Control-Allow-
// Origin: *). The Next.js rewrites stay configured as a fallback for
// when the var isn't set (production-by-default, same-origin deploys).

import type { Brief, PebblePlan } from "./state";

const ENGINE_BASE: string = (process.env.NEXT_PUBLIC_PEBBLE_ENGINE_URL || "").replace(/\/+$/, "");

function engineUrl(path: string): string {
  // path always starts with /, ENGINE_BASE has no trailing slash, so concat works.
  return ENGINE_BASE ? `${ENGINE_BASE}${path}` : path;
}

export class PlanLimitError extends Error {
  upgradeUrl: string;
  constructor(message: string, upgradeUrl: string) {
    super(message);
    this.name = "PlanLimitError";
    this.upgradeUrl = upgradeUrl;
  }
}

async function postJSON<T>(path: string, body: unknown): Promise<T> {
  const resp = await fetch(engineUrl(path), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const text = await resp.text();
  let json: unknown;
  try { json = JSON.parse(text); } catch { json = { error: text || "non-json response" }; }
  if (!resp.ok) {
    const payload = json as { error?: string; upgrade_url?: string };
    const err = payload.error || `HTTP ${resp.status}`;
    if (resp.status === 402 && payload.upgrade_url) {
      throw new PlanLimitError(err, payload.upgrade_url);
    }
    throw new Error(err);
  }
  return json as T;
}

async function getJSON<T>(path: string): Promise<T> {
  const resp = await fetch(engineUrl(path));
  const text = await resp.text();
  let json: unknown;
  try { json = JSON.parse(text); } catch { json = { error: text || "non-json response" }; }
  if (!resp.ok) {
    const err = (json as { error?: string }).error || `HTTP ${resp.status}`;
    throw new Error(err);
  }
  return json as T;
}

async function deleteJSON<T>(path: string): Promise<T> {
  const resp = await fetch(engineUrl(path), { method: "DELETE" });
  const text = await resp.text();
  let json: unknown;
  try { json = JSON.parse(text); } catch { json = { error: text || "non-json response" }; }
  if (!resp.ok) {
    const err = (json as { error?: string }).error || `HTTP ${resp.status}`;
    throw new Error(err);
  }
  return json as T;
}

// ---------- SSE build streaming (new) ----------------------------------------

/**
 * Discriminated union of all SSE events emitted by /api/generate-stream.
 * The ``done`` event carries the full GenerateResponse payload.
 */
export type SSEEvent =
  | { type: "started";    data: { slug: string } }
  | { type: "industry";   data: { key: string | null } }
  | { type: "style";      data: { dna_label: string; dna_id: string } }
  | { type: "generating"; data: { model: string; max_tokens: number } }
  | { type: "writing";    data: { file_count: number } }
  | { type: "evaluating"; data: Record<string, never> }
  | { type: "done";       data: GenerateResponse }
  | { type: "error";      data: { error: string } };

/**
 * Stream a site build via /api/generate-stream (POST + SSE).
 *
 * Calls ``onEvent`` for each SSE frame, resolves with the GenerateResponse
 * from the ``done`` event, or rejects on ``error`` or network failure.
 *
 * Uses fetch + ReadableStream rather than EventSource because EventSource
 * only supports GET requests.
 *
 * The engine URL must be set to a direct connection
 * (NEXT_PUBLIC_PEBBLE_ENGINE_URL=http://localhost:8000) in dev so SSE
 * bypasses the Next.js proxy, which buffers the stream.
 */
export async function streamGenerateSite(
  brief: Brief,
  onEvent: (e: SSEEvent) => void,
): Promise<GenerateResponse> {
  // Include the Supabase session token when available so the engine can
  // associate the build with the authenticated user (publish limit check,
  // email drip). Auth is optional — anonymous builds still work.
  let authHeader: Record<string, string> = {};
  try {
    const { createClient } = await import("./supabase/client");
    const supabase = createClient();
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
      authHeader = { "Authorization": `Bearer ${session.access_token}` };
    }
  } catch {
    // No Supabase available — proceed as anonymous
  }

  const resp = await fetch(engineUrl("/api/generate-stream"), {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader },
    body: JSON.stringify(brief),
  });

  if (!resp.ok) {
    const text = await resp.text();
    let payload: { error?: string; upgrade_url?: string };
    try { payload = JSON.parse(text); } catch { payload = { error: text || `HTTP ${resp.status}` }; }
    const err = payload.error || `HTTP ${resp.status}`;
    if (resp.status === 402 && payload.upgrade_url) {
      throw new PlanLimitError(err, payload.upgrade_url);
    }
    throw new Error(err);
  }

  const reader = resp.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    // SSE blocks are separated by \n\n. Split, keep the last incomplete one.
    const blocks = buffer.split("\n\n");
    buffer = blocks.pop() ?? "";

    for (const block of blocks) {
      if (!block.trim()) continue;
      let eventType = "";
      let dataStr = "";
      for (const line of block.split("\n")) {
        if (line.startsWith("event: ")) eventType = line.slice(7).trim();
        else if (line.startsWith("data: ")) dataStr = line.slice(6).trim();
      }
      if (!eventType || !dataStr) continue;
      let data: unknown;
      try { data = JSON.parse(dataStr); } catch { continue; }
      const event = { type: eventType, data } as SSEEvent;
      onEvent(event);
      if (eventType === "done") return data as GenerateResponse;
      if (eventType === "error") throw new Error((data as { error: string }).error || "Build failed");
    }
  }

  throw new Error("Stream ended without a done event");
}

// ---------- /api/plan + /api/generate (existing) ----------------------------

export type PlanResponse = {
  plan: PebblePlan;
  industry_key: string | null;
  dna_id: string | null;
};

export async function fetchPlan(brief: Brief): Promise<PlanResponse> {
  return postJSON<PlanResponse>("/api/plan", brief);
}

export type DevServerInfo = {
  enabled?: boolean;
  port?: number | null;
  pid?: number | null;
  url?: string | null;
  errors?: string[];
};

export type GenerateResponse = {
  slug: string;
  preview_url: string;
  saved_to: string;
  files_written: string[];
  file_count: number;
  elapsed_seconds: number;
  industry_intel_key: string | null;
  // Populated when PEBBLE_AUTO_RUN=true and the engine started `next dev`.
  // Generated sites are Next.js apps with no static index.html — preview_url
  // (/preview/<slug>/) 404s for them. The live dev_server.url loads via the
  // running `next dev` process. Falls back to preview_url when absent.
  dev_server?: DevServerInfo;
};

export async function generateSite(brief: Brief): Promise<GenerateResponse> {
  return postJSON<GenerateResponse>("/api/generate", brief);
}

type PreviewBuild = {
  preview_url?: string;
  dev_server?: DevServerInfo | null;
};

// Prefer the running `next dev` URL over the static preview path. The
// preview path serves files from output/<slug>/site/ — fine for plain
// HTML but 404s for Next.js sites (no compiled index.html on disk).
// Falls back to preview_url, then to "about:blank" as a last resort.
export function pickPreviewUrl(build: PreviewBuild | null | undefined): string {
  const devUrl = build?.dev_server?.url;
  if (typeof devUrl === "string" && devUrl.length > 0) return devUrl;
  if (build?.preview_url) return build.preview_url;
  return "about:blank";
}

// ---------- /api/projects (new) --------------------------------------------

export type ProjectSummary = {
  slug: string;
  business_name: string;
  business_type: string | null;
  built_at: string;
  file_count: number;
  starred: boolean;
  preview_url: string;
  design_dna: string | null;
  publish?: {
    kind:        "zip" | "cloudflare";
    url:         string;
    deployed_at: string;
  } | null;
  domain?: Partial<DomainRecord> & { host: string; status: "pending" | "active" | "error" } | null;
  inbox?: { total: number; unread: number } | null;
};

export async function listProjects(): Promise<{ projects: ProjectSummary[]; count: number }> {
  return getJSON("/api/projects");
}

export async function toggleStar(slug: string, starred?: boolean): Promise<{ slug: string; starred: boolean }> {
  return postJSON(`/api/projects/${encodeURIComponent(slug)}/star`,
    typeof starred === "boolean" ? { starred } : {});
}

// ---------- /api/history + /api/rollback (new) -----------------------------

export type HistorySnapshot = {
  snapshot_id: string;
  written_at: string;
  reason: string;            // "generate" | "refine-friendlier" | "visual-edit-text" | "restore" | etc
  source: string;
  files_count: number;
  relative_path: string;
};

export async function fetchHistory(slug: string): Promise<{ slug: string; snapshots: HistorySnapshot[]; count: number }> {
  return getJSON(`/api/projects/${encodeURIComponent(slug)}/history`);
}

export async function rollback(slug: string, snapshot_id: string): Promise<{ slug: string; snapshot_id: string; files_restored: number }> {
  return postJSON("/api/rollback", { slug, snapshot_id });
}

// ---------- /api/refine (new) ----------------------------------------------

export type RefinementId =
  | "simpler" | "colors"                    // deterministic, free
  | "friendlier" | "professional" | "booking"; // LLM-backed, billable

export type RefineResponse = {
  slug: string;
  refinement_id: RefinementId;
  files_changed: string[];
  kind: "deterministic" | "llm";
  billable: boolean;
  snapshot_id: string | null;
  elapsed_seconds: number;
  details: string;
  applied_at: string;
};

export async function refine(slug: string, refinement_id: RefinementId): Promise<RefineResponse> {
  return postJSON("/api/refine", { slug, refinement_id });
}

// ---------- /api/visual-edit (new) -----------------------------------------

export type VisualEditOp = "text" | "color" | "font-size";

// pebble_id is the data-pebble-id attribute injected at generate-time. When
// provided, the engine does a surgical edit scoped to that exact element.
// When absent (older builds without injection), the engine falls back to
// the legacy substring/selector-hint heuristics.
export type VisualEditBody =
  | { slug: string; op: "text"; pebble_id?: string; original_text: string; new_text: string }
  | { slug: string; op: "color"; pebble_id?: string; selector_hint?: string; original_text?: string; new_color: string }
  | { slug: string; op: "font-size"; pebble_id?: string; selector_hint?: string; original_text?: string; new_font_size?: string; delta: number };

export type VisualEditResponse = {
  slug: string;
  op: VisualEditOp;
  files_changed: string[];
  ambiguous: boolean;
  billable: false;
  snapshot_id: string | null;
  used_manifest: boolean;
  applied_at: string;
};

export async function visualEdit(body: VisualEditBody): Promise<VisualEditResponse> {
  return postJSON("/api/visual-edit", body);
}

// ---------- Iframe-bridge message shape (postMessage from /preview) --------

export type PebbleSelectMessage = {
  type: "pebble-select";
  tag: string;
  id: string;
  pebble_id: string;     // empty string when the build pre-dates id injection
  className: string;
  text: string;
  rect: { x: number; y: number; w: number; h: number };
  style: {
    color: string;
    fontSize: string;
    fontFamily: string;
    background: string;
  };
};

export type PebbleReadyMessage = {
  type:    "pebble-ready";
  version: number;
};

export function isPebbleSelectMessage(data: unknown): data is PebbleSelectMessage {
  if (!data || typeof data !== "object") return false;
  const d = data as Record<string, unknown>;
  return d.type === "pebble-select" && typeof d.tag === "string";
}

export function isPebbleReadyMessage(data: unknown): data is PebbleReadyMessage {
  if (!data || typeof data !== "object") return false;
  const d = data as Record<string, unknown>;
  return d.type === "pebble-ready";
}

// ---------- /api/migrate (new — site migration entry point) ----------------

export type MigrationExtract = {
  url:                 string;
  final_url:           string;
  title:               string;
  meta_description:    string;
  og_title:            string;
  og_description:      string;
  headings:            string[];
  nav_links:           string[];
  phone:               string;
  emails:              string[];
  image_count:         number;
  image_hosts:         string[];
  color_hints:         string[];
  text_sample:         string;
  business_name_guess: string;
  business_type_guess: string;
  error:               string | null;
  raw_bytes:           number;
};

export type MigrateBriefPartial = {
  business_name:  string;
  business_type:  string;
  extra_context:  string;
  _migrated_from: string;
};

export type MigrateResponse = {
  url:           string;
  extract:       MigrationExtract;
  brief_partial: MigrateBriefPartial;
  ok:            boolean;
  error:         string | null;
};

export async function migrateFromUrl(url: string): Promise<MigrateResponse> {
  return postJSON("/api/migrate", { url });
}

// ---------- /api/inspire (style-direction sibling of /api/migrate) --------

export type InspirationExtract = {
  url:           string;
  final_url:     string;
  error:         string | null;
  raw_bytes:     number;
  title:         string;
  headline:      string;
  subheading:    string;
  palette:       {
    primary:    string;
    accent:     string;
    background: string;
    all:        string[];
  };
  typography:    {
    display:      string;
    body:         string;
    all_families: string[];
  };
  vibe:          {
    is_dark:     boolean;
    is_minimal:  boolean;
    color_count: number;
    descriptors: string[];
  };
  suggested_dna: {
    id:     string;
    label:  string;
    score:  number;
    reason: string;
  };
};

export type InspireBriefPartial = {
  extra_context:     string;
  _inspired_by:      string;
  _inspire_dna_hint: string;
};

export type InspireResponse = {
  url:           string;
  extract:       InspirationExtract;
  brief_partial: InspireBriefPartial;
  ok:            boolean;
  error:         string | null;
};

export async function inspireFromUrl(url: string): Promise<InspireResponse> {
  return postJSON("/api/inspire", { url });
}

// ---------- /api/blocks (DNA-themed drop-in sections) ---------------------

export type BlockCategory = "social-proof" | "conversion" | "explainer" | "monetization" | "growth";

export type BlockListing = {
  id:          string;
  label:       string;
  category:    BlockCategory;
  description: string;
  icon:        string;          // lucide-react icon NAME (e.g. "Coins")
};

export async function listBlocks(): Promise<{ blocks: BlockListing[]; count: number }> {
  return getJSON("/api/blocks");
}

export type BlockInsertResponse = {
  slug:           string;
  block_id:       string;
  component_name: string;
  files_written:  string[];
  files_modified: string[];
  snapshot_id:    string | null;
  position:       string;
  page_file:      string;
  billable:       false;          // always free — the whole point of blocks
  dna_id:         string;
  dna_label:      string;
  applied_at:     string;
};

export async function insertBlock(slug: string, block_id: string): Promise<BlockInsertResponse> {
  return postJSON(`/api/projects/${encodeURIComponent(slug)}/blocks/insert`, { block_id });
}

// ---------- /api/usage + DELETE /api/projects/<slug> -----------------------

export type UsageRow = {
  slug:                string;
  built_at:            string | null;
  input_tokens:        number;
  output_tokens:       number;
  estimated_cost_usd:  number;
  billable:            boolean;
  model:               string | null;
};

export type UsageSummary = {
  projects:                  number;
  total_input_tokens:        number;
  total_output_tokens:       number;
  total_estimated_cost_usd:  number;
  by_project:                UsageRow[];
};

export async function fetchUsage(): Promise<UsageSummary> {
  return getJSON("/api/usage");
}

// ---------- /api/activity (new) --------------------------------------------

export type ActivityRow = {
  slug:          string;
  business_name: string;
  snapshot_id:   string;
  reason:        string;
  source:        string;
  written_at:    string;
  files_count:   number;
};

export async function fetchActivity(): Promise<{ activity: ActivityRow[]; count: number }> {
  return getJSON("/api/activity");
}

// ---------- /api/forms/<slug> + /api/projects/<slug>/inbox -----------------

export type Submission = {
  id:           string;
  slug:         string;
  received_at:  string;
  fields:       Record<string, string>;
  ip_hash?:     string | null;
  user_agent?:  string | null;
  referrer?:    string | null;
  read?:        boolean;
};

export async function submitForm(slug: string, fields: Record<string, string>): Promise<{ ok: boolean; id: string }> {
  return postJSON(`/api/forms/${encodeURIComponent(slug)}`, fields);
}

export async function fetchInbox(slug: string): Promise<{ slug: string; submissions: Submission[]; count: number; unread: number }> {
  return getJSON(`/api/projects/${encodeURIComponent(slug)}/inbox`);
}

export async function markSubmissionRead(slug: string, id: string, read: boolean = true): Promise<Submission> {
  return postJSON(`/api/projects/${encodeURIComponent(slug)}/inbox/${encodeURIComponent(id)}/read`, { read });
}

// ---------- /api/projects/<slug>/forms/webhook ------------------------------

export type WebhookConfig = {
  url:            string;
  configured_at:  string;
};

export type WebhookConfigResponse = {
  slug:        string;
  configured:  boolean;
  webhook:     WebhookConfig | null;
};

export async function fetchWebhookConfig(slug: string): Promise<WebhookConfigResponse> {
  return getJSON(`/api/projects/${encodeURIComponent(slug)}/forms/webhook`);
}

export async function setWebhookConfig(slug: string, url: string): Promise<WebhookConfigResponse> {
  return postJSON(`/api/projects/${encodeURIComponent(slug)}/forms/webhook`, { url });
}

export async function clearWebhookConfig(slug: string): Promise<{ slug: string; removed: boolean; configured: false }> {
  return deleteJSON(`/api/projects/${encodeURIComponent(slug)}/forms/webhook`);
}

// ---------- /api/projects/<slug>/forms/autoresponder -----------------------

export type AutoresponderConfig = {
  enabled:        boolean;
  subject:        string;
  body:           string;
  reply_field:    string;
  configured_at:  string;
};

export type AutoresponderConfigResponse = {
  slug:           string;
  autoresponder:  AutoresponderConfig;
};

export type AutoresponderUpdate = {
  enabled:        boolean;
  subject?:       string;
  body?:          string;
  reply_field?:   string;
};

export async function fetchAutoresponder(slug: string): Promise<AutoresponderConfigResponse> {
  return getJSON(`/api/projects/${encodeURIComponent(slug)}/forms/autoresponder`);
}

export async function saveAutoresponder(slug: string, update: AutoresponderUpdate): Promise<AutoresponderConfigResponse> {
  return postJSON(`/api/projects/${encodeURIComponent(slug)}/forms/autoresponder`, update);
}

export async function clearAutoresponder(slug: string): Promise<{ slug: string; removed: boolean }> {
  return deleteJSON(`/api/projects/${encodeURIComponent(slug)}/forms/autoresponder`);
}

// ---------- /api/projects/<slug>/forms/attachment-url (Phase 2) ------------

export type AttachmentSignedUrl = {
  url:        string;
  expires_in: number;   // seconds
  path:       string;
};

/**
 * Fetch a short-lived signed URL for a stored form attachment. Used
 * by the inbox detail view when rendering a download link for a
 * private-bucket Supabase Storage object.
 *
 * The path MUST start with the project's slug (the engine validates
 * this server-side; never trust a path the visitor wrote into the
 * form to point at an object outside the project).
 */
export async function fetchAttachmentSignedUrl(slug: string, path: string): Promise<AttachmentSignedUrl> {
  return postJSON(
    `/api/projects/${encodeURIComponent(slug)}/forms/attachment-url`,
    { path },
  );
}

// ---------- /api/account/delete (GDPR — Ch 7.7) ---------------------------

export type AccountDeleteResponse = {
  ok:      boolean;
  deleted: boolean;
  user_id: string;
  next:    string;    // path to redirect to after client-side signOut
};

/**
 * GDPR-style account deletion. Pulls the current Supabase access
 * token client-side, POSTs to the engine which validates the token
 * and admin-deletes the user (cascades to public.profiles via FK).
 *
 * On success, callers MUST follow up with:
 *   await supabase.auth.signOut();
 *   router.push(result.next);
 *
 * The engine doesn't (and can't) clear the v3-side Supabase cookies
 * — that's a client-only API.
 */
export async function deleteAccount(): Promise<AccountDeleteResponse> {
  // Lazy-import the supabase client so the engine-only build paths
  // (e.g. tests that exercise lib/api.ts in isolation) don't pull
  // the whole @supabase/ssr graph.
  const { createClient } = await import("./supabase/client");
  const supabase = createClient();
  const { data: { session } } = await supabase.auth.getSession();
  if (!session?.access_token) {
    throw new Error("Not signed in.");
  }
  const resp = await fetch(engineUrl("/api/account/delete"), {
    method:  "POST",
    headers: {
      "Content-Type":  "application/json",
      "Authorization": `Bearer ${session.access_token}`,
    },
  });
  const text = await resp.text();
  let json: unknown;
  try { json = JSON.parse(text); } catch { json = { error: text || "non-json response" }; }
  if (!resp.ok) {
    const err = (json as { error?: string }).error || `HTTP ${resp.status}`;
    throw new Error(err);
  }
  return json as AccountDeleteResponse;
}

// ---------- /api/checkout + /api/billing (Stripe) --------------------------

export type CheckoutSessionResponse = {
  url:        string;
  session_id: string;
};

export type BillingPortalResponse = {
  url: string;
};

export type SubscriptionState = {
  plan:               "starter" | "pro" | null;
  status:             string | null;   // "active" | "past_due" | "canceled" | ... | null
  current_period_end: number | null;   // unix seconds, or null
};

/**
 * Helper that does the "get current JWT, send Authorization: Bearer" dance
 * for the billing endpoints (which are auth-gated via require_user). All
 * billing routes need this, so DRY it.
 */
async function authedPostJSON<T>(path: string, body: unknown): Promise<T> {
  const { createClient } = await import("./supabase/client");
  const supabase = createClient();
  const { data: { session } } = await supabase.auth.getSession();
  if (!session?.access_token) {
    throw new Error("Not signed in.");
  }
  const resp = await fetch(engineUrl(path), {
    method:  "POST",
    headers: {
      "Content-Type":  "application/json",
      "Authorization": `Bearer ${session.access_token}`,
    },
    body: JSON.stringify(body),
  });
  const text = await resp.text();
  let json: unknown;
  try { json = JSON.parse(text); } catch { json = { error: text || "non-json response" }; }
  if (!resp.ok) {
    const err = (json as { error?: string }).error || `HTTP ${resp.status}`;
    throw new Error(err);
  }
  return json as T;
}

/**
 * Open a Stripe Checkout session for the selected plan. Returns the
 * hosted-payment URL; the caller is responsible for the actual redirect
 * (typically `window.location.href = url`).
 *
 * Auth: requires a logged-in Supabase user. The engine looks the user
 * up from the bearer JWT and stamps their id on the Checkout Session so
 * the Stripe webhook can route subscription events back to this Pebble
 * account.
 */
export async function createCheckoutSession(plan: "starter" | "pro"): Promise<CheckoutSessionResponse> {
  return authedPostJSON<CheckoutSessionResponse>("/api/checkout/create-session", { plan });
}

/**
 * Mint a Stripe Customer Portal session for the current user. Returns
 * the portal URL; the caller redirects the browser there.
 *
 * Throws "No active subscription" if the user has never subscribed
 * (the engine returns 404 in that case so the UI can route them to
 * the pricing page instead).
 */
export async function openBillingPortal(): Promise<BillingPortalResponse> {
  return authedPostJSON<BillingPortalResponse>("/api/billing/portal", {});
}

/**
 * Get the current user's subscription state — plan, status, renewal date.
 * Returns ``{plan: null, ...}`` for users who have never subscribed
 * (instead of throwing) so the UI can branch on the field.
 */
export async function fetchSubscription(): Promise<SubscriptionState> {
  const { createClient } = await import("./supabase/client");
  const supabase = createClient();
  const { data: { session } } = await supabase.auth.getSession();
  if (!session?.access_token) {
    throw new Error("Not signed in.");
  }
  const resp = await fetch(engineUrl("/api/billing/subscription"), {
    headers: { "Authorization": `Bearer ${session.access_token}` },
  });
  const text = await resp.text();
  let json: unknown;
  try { json = JSON.parse(text); } catch { json = { error: text || "non-json response" }; }
  if (!resp.ok) {
    const err = (json as { error?: string }).error || `HTTP ${resp.status}`;
    throw new Error(err);
  }
  return json as SubscriptionState;
}

// ---------- /api/track + /api/projects/<slug>/analytics -------------------

export type AnalyticsSummary = {
  slug:                string;
  window_days:         number;
  total_views:         number;
  approx_visitors:     number;
  top_paths:           { path: string; views: number }[];
  top_referrer_hosts:  { host: string; views: number }[];
  by_day:              { date: string; views: number }[];
};

export async function fetchAnalytics(slug: string): Promise<AnalyticsSummary> {
  return getJSON(`/api/projects/${encodeURIComponent(slug)}/analytics`);
}

export async function trackPageView(slug: string, path: string, referrer?: string): Promise<{ ok: boolean; recorded: boolean }> {
  return postJSON(`/api/track/${encodeURIComponent(slug)}`, { path, referrer });
}

export async function deleteSubmission(slug: string, id: string): Promise<{ slug: string; id: string; deleted: boolean }> {
  const resp = await fetch(`/api/projects/${encodeURIComponent(slug)}/inbox/${encodeURIComponent(id)}`, { method: "DELETE" });
  const text = await resp.text();
  let json: unknown;
  try { json = JSON.parse(text); } catch { json = { error: text || "non-json" }; }
  if (!resp.ok) {
    const err = (json as { error?: string }).error || `HTTP ${resp.status}`;
    throw new Error(err);
  }
  return json as { slug: string; id: string; deleted: boolean };
}

// ---------- /api/publish (new) ---------------------------------------------

export type PublishKind = "zip" | "cloudflare";
export type PublishDest = "auto" | "zip" | "cloudflare";

export type PublishResponse = {
  slug:                 string;
  kind:                 PublishKind;
  url:                  string;             // download URL or live URL
  deployed_at:          string;
  bytes_published:      number;
  files_published:      number;
  snapshot_id?:         string | null;
  deployment_id?:       string | null;
  project_name?:        string | null;
  note?:                string | null;
  cloudflare_setup_md?: string | null;
  elapsed_seconds?:     number;
};

export async function publishSite(slug: string, dest: PublishDest = "auto"): Promise<PublishResponse> {
  return postJSON("/api/publish", { slug, dest });
}

export type PublishStateResponse = {
  slug:    string;
  current: PublishResponse | null;
  history: PublishResponse[];
};

export async function fetchPublishState(slug: string): Promise<PublishStateResponse> {
  return getJSON(`/api/projects/${encodeURIComponent(slug)}/publish`);
}

// ---------- /api/projects/<slug>/domain ------------------------------------

export type DomainRecord = {
  host:         string;
  status:       "pending" | "active" | "error";
  set_at:       string;
  cname_target: string;
  cname_record: string;
  error?:       string | null;
};

export type DomainResponse = {
  slug:                  string;
  domain:                DomainRecord | null;
  cloudflare_configured: boolean;
  cloudflare_setup_md?:  string | null;
};

export async function fetchDomain(slug: string): Promise<DomainResponse> {
  return getJSON(`/api/projects/${encodeURIComponent(slug)}/domain`);
}

export async function setDomain(slug: string, host: string): Promise<DomainResponse> {
  return postJSON(`/api/projects/${encodeURIComponent(slug)}/domain`, { host });
}

export async function removeDomain(slug: string): Promise<{ slug: string; removed: DomainRecord }> {
  const resp = await fetch(`/api/projects/${encodeURIComponent(slug)}/domain`, { method: "DELETE" });
  const text = await resp.text();
  let json: unknown;
  try { json = JSON.parse(text); } catch { json = { error: text || "non-json response" }; }
  if (!resp.ok) {
    const err = (json as { error?: string }).error || `HTTP ${resp.status}`;
    throw new Error(err);
  }
  return json as { slug: string; removed: DomainRecord };
}

export async function deleteProject(slug: string): Promise<{ slug: string; deleted: boolean }> {
  return deleteJSON(`/api/projects/${encodeURIComponent(slug)}`);
}

// ---------- /api/account/* --------------------------------------------------

export type ProfileResponse = {
  id:                     string;
  email:                  string;
  first_name:             string | null;
  display_name:           string | null;
  timezone:               string;
  plan_tier:              string;
  deletion_scheduled_for: string | null;
};

export type ProfileUpdates = {
  first_name?:   string | null;
  display_name?: string | null;
  timezone?:     string;
};
