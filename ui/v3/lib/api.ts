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

export type VisualEditBody =
  | { slug: string; op: "text"; original_text: string; new_text: string }
  | { slug: string; op: "color"; selector_hint?: string; original_text?: string; new_color: string }
  | { slug: string; op: "font-size"; selector_hint?: string; original_text?: string; delta: number };

export type VisualEditResponse = {
  slug: string;
  op: VisualEditOp;
  files_changed: string[];
  ambiguous: boolean;
  billable: false;
  snapshot_id: string | null;
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

export function isPebbleSelectMessage(data: unknown): data is PebbleSelectMessage {
  if (!data || typeof data !== "object") return false;
  const d = data as Record<string, unknown>;
  return d.type === "pebble-select" && typeof d.tag === "string";
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
