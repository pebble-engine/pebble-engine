"use client";

/**
 * Auth menu — drop-in chip for the top nav. Shows "Sign in" when signed
 * out, the user's email + a dropdown with Sign out when signed in.
 */

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { ChevronDown, LogOut, User } from "lucide-react";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";
import { useAuth } from "@/components/auth-provider";

export function AuthMenu() {
  const { user, loading, signOut } = useAuth();
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!open) return;
    function onDocClick(e: MouseEvent) {
      if (!containerRef.current?.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, [open]);

  if (loading) {
    return (
      <span className="h-9 w-9 rounded-full border border-border bg-muted animate-pulse" aria-hidden />
    );
  }

  if (!user) {
    return (
      <div className="flex items-center gap-2">
        <Link
          href="/login"
          className={`${interactions.link} ${type.label} inline-flex items-center rounded-full px-3 py-2 text-muted-foreground`}
        >
          Sign in
        </Link>
        <Link
          href="/signup"
          className={`${interactions.button} ${type.label} inline-flex items-center rounded-full bg-primary px-3 py-2 text-primary-foreground`}
        >
          Sign up
        </Link>
      </div>
    );
  }

  const initial = user.email.charAt(0).toUpperCase();

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className={`${interactions.chip} ${type.label} inline-flex items-center gap-2 rounded-full border border-border bg-card pl-1 pr-3 py-1 text-foreground`}
        aria-haspopup="menu"
        aria-expanded={open}
      >
        <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-primary text-primary-foreground font-semibold text-xs">
          {initial}
        </span>
        <span className="hidden sm:inline max-w-[160px] truncate">{user.email}</span>
        <ChevronDown className={`h-3.5 w-3.5 text-muted-foreground transition-transform ${open ? "rotate-180" : ""}`} />
      </button>

      {open && (
        <div
          role="menu"
          className="absolute right-0 mt-2 w-56 rounded-xl border border-border bg-card shadow-[var(--shadow-1)] overflow-hidden z-50"
        >
          <div className="px-3 py-2 border-b border-border">
            <p className={type.caption}>Signed in as</p>
            <p className={`${type.label} text-foreground truncate`}>{user.email}</p>
          </div>
          <Link
            href="/dashboard"
            className={`${interactions.chip} ${type.body.s} flex items-center gap-2 px-3 py-2 text-foreground`}
            onClick={() => setOpen(false)}
          >
            <User className="h-4 w-4 text-muted-foreground" />
            My sites
          </Link>
          <button
            type="button"
            onClick={async () => {
              setOpen(false);
              await signOut();
            }}
            className={`${interactions.chip} ${type.body.s} w-full flex items-center gap-2 px-3 py-2 text-foreground text-left border-t border-border`}
          >
            <LogOut className="h-4 w-4 text-muted-foreground" />
            Sign out
          </button>
        </div>
      )}
    </div>
  );
}
