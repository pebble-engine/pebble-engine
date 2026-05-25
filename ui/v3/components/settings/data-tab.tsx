"use client";

/**
 * Data tab — GDPR Article 20 export (B3) + delete account (A3 flow).
 */

import { useState } from "react";
import { createBrowserClient } from "@supabase/ssr";

import { DeleteAccountSection } from "./delete-account-section";

const ENGINE_BASE = (process.env.NEXT_PUBLIC_PEBBLE_ENGINE_URL || "").replace(
  /\/+$/,
  ""
);

export function DataTab() {
  const [exportStatus, setExportStatus] = useState<
    "idle" | "requesting" | "queued" | "error"
  >("idle");
  const [exportMessage, setExportMessage] = useState<string>("");

  async function requestExport() {
    setExportStatus("requesting");
    setExportMessage("");
    try {
      const supabase = createBrowserClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
      );
      const { data } = await supabase.auth.getSession();
      const token = data.session?.access_token;
      if (!token) {
        setExportStatus("error");
        setExportMessage("Please sign in again.");
        return;
      }
      const resp = await fetch(`${ENGINE_BASE}/api/account/export-request`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: "{}",
      });
      const body = await resp.json();
      if (resp.ok) {
        setExportStatus("queued");
        setExportMessage(body.message || "Export is being prepared.");
      } else {
        setExportStatus("error");
        setExportMessage(body.error || "Could not request export.");
      }
    } catch (e: unknown) {
      setExportStatus("error");
      setExportMessage(
        e instanceof Error ? e.message : "Network error."
      );
    }
  }

  return (
    <div className="space-y-10">
      <div>
        <h2 className="mb-1 text-lg font-medium">Export your data</h2>
        <p className="mb-4 text-sm text-muted-foreground">
          Download all your projects, account information, and activity log as a
          single ZIP. Required under GDPR Article 20. The download link will be
          emailed and expires in 24 hours.
        </p>
        <button
          onClick={requestExport}
          disabled={
            exportStatus === "requesting" || exportStatus === "queued"
          }
          className="rounded-md border bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-60"
        >
          {exportStatus === "requesting"
            ? "Requesting…"
            : exportStatus === "queued"
            ? "Email sent"
            : "Export my data"}
        </button>
        {exportMessage && (
          <p
            className={`mt-2 text-sm ${
              exportStatus === "error"
                ? "text-destructive"
                : "text-muted-foreground"
            }`}
          >
            {exportMessage}
          </p>
        )}
      </div>

      <DeleteAccountSection />
    </div>
  );
}
