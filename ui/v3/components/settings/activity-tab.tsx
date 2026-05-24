"use client";

/**
 * Activity tab — placeholder for B2.
 * B2 wires the actual /api/account/activity endpoint.
 */

export function ActivityTab() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="mb-1 text-lg font-medium">Account activity</h2>
        <p className="text-sm text-muted-foreground">
          A log of security-sensitive actions on your account: password changes,
          email changes, account-deletion requests, and sign-ins from new devices.
        </p>
      </div>
      <div className="rounded-lg border border-dashed p-8 text-center text-sm text-muted-foreground">
        Account activity will appear here once you take security-sensitive actions
        (password change, email change, etc.).
      </div>
    </div>
  );
}
