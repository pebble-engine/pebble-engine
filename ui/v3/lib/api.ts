// Thin client for the Pebble engine. Calls go through Next.js' rewrites
// (configured in next.config.ts) to localhost:8000 in dev.

import type { Brief, PebblePlan } from "./state";

async function postJSON<T>(path: string, body: unknown): Promise<T> {
  const resp = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
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

async function getJSON<T>(path: string): Promise<T> {
  const resp = await fetch(path);
  const text = await resp.text();
  let json: unknown;
  try { json = JSON.parse(text); } catch { json = { error: text || "non-json response" }; }
  if (!resp.ok) {
    const err = (json as { error?: string }).error || `HTTP ${resp.status}`;
    throw new Error(err);
  }
  return json as T;
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

export type GenerateResponse = {
  slug: string;
  preview_url: string;
  saved_to: string;
  files_written: string[];
  file_count: number;
  elapsed_seconds: number;
  industry_intel_key: string | null;
};

export async function generateSite(brief: Brief): Promise<GenerateResponse> {
  return postJSON<GenerateResponse>("/api/generate", brief);
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

async function deleteJSON<T>(path: string): Promise<T> {
  const resp = await fetch(path, { method: "DELETE" });
  const text = await resp.text();
  let json: unknown;
  try { json = JSON.parse(text); } catch { json = { error: text || "non-json response" }; }
  if (!resp.ok) {
    const err = (json as { error?: string }).error || `HTTP ${resp.status}`;
    throw new Error(err);
  }
  return json as T;
}

export async function deleteProject(slug: string): Promise<{ slug: string; deleted: boolean }> {
  return deleteJSON(`/api/projects/${encodeURIComponent(slug)}`);
}
