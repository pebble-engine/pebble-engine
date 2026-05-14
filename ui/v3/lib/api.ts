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
