"use client";

/**
 * Data tab — export placeholder (B3) + delete account (A3 flow).
 */

import { DeleteAccountSection } from "./delete-account-section";

export function DataTab() {
  return (
    <div className="space-y-10">
      {/* Export — placeholder for B3 */}
      <div>
        <h2 className="mb-1 text-lg font-medium">Export your data</h2>
        <p className="mb-4 text-sm text-muted-foreground">
          Download all your projects, account information, and activity log as a
          single ZIP. Required under GDPR Article 20.
        </p>
        <button
          disabled
          className="rounded-md border bg-muted px-4 py-2 text-sm opacity-60"
        >
          Export my data (coming soon)
        </button>
      </div>

      {/* Delete account — existing functionality */}
      <DeleteAccountSection />
    </div>
  );
}
