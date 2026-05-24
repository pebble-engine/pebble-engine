"use client";

/**
 * Peblet Shortcuts — one-tap actions surface (2026-05-23).
 *
 * Marc's brief: "all searchable items should be with this chatbot — I
 * dont want people feeling lost." Chat is the conversational path;
 * Shortcuts is the verb-first path. Tap a row and the action happens
 * (or the confirmation panel appears). No typing required.
 *
 * Groups:
 *   - Navigate — jump to any app destination
 *   - Build    — start something new
 *   - Manage   — billing, settings, danger zone
 *
 * Destructive intents (cancel subscription, delete account) route
 * to /settings rather than firing here — the chat thread is the only
 * place we render a confirmation panel, and Shortcuts is meant to be
 * frictionless. If a user wants to cancel they can find the button
 * on the settings page itself.
 */

import { useRouter } from "next/navigation";
import {
  Home,
  FolderOpen,
  Compass,
  Plug,
  Users,
  Settings,
  Sparkles,
  CreditCard,
  LifeBuoy,
  Rocket,
  type LucideIcon,
} from "lucide-react";

type ShortcutGroup = {
  label: string;
  items: Array<{
    label: string;
    description: string;
    icon: LucideIcon;
    href: string;
  }>;
};

const GROUPS: ShortcutGroup[] = [
  {
    label: "Navigate",
    items: [
      { label: "Dashboard",         description: "Your home base",              icon: Home,       href: "/dashboard" },
      { label: "Projects",          description: "Every site you've built",     icon: FolderOpen, href: "/projects" },
      { label: "Templates",         description: "Pick a starting point",       icon: Compass,    href: "/templates" },
      { label: "Integrations",      description: "Stripe, Resend, Calendly…",    icon: Plug,       href: "/integrations" },
      { label: "Community",         description: "Other builders + partners",   icon: Users,      href: "/community" },
    ],
  },
  {
    label: "Build",
    items: [
      { label: "Start something new", description: "Talk through a new build",     icon: Sparkles, href: "/workspace#phase=welcome" },
      { label: "Launch a project",    description: "Publish & domain setup help", icon: Rocket,   href: "/dashboard" },
    ],
  },
  {
    label: "Manage",
    items: [
      { label: "Account settings", description: "Profile, plan, danger zone", icon: Settings,    href: "/settings" },
      { label: "Billing",          description: "Payment method, invoices",  icon: CreditCard,  href: "/settings" },
      { label: "Help & support",   description: "Email us, read the docs",   icon: LifeBuoy,    href: "/trust" },
    ],
  },
];

export function PebletShortcuts() {
  const router = useRouter();
  return (
    <div className="flex-1 overflow-y-auto px-4 py-4 space-y-5">
      {GROUPS.map((group) => (
        <section key={group.label} className="space-y-1.5">
          <h3 className="text-[10px] uppercase tracking-widest font-semibold text-muted-foreground px-1">
            {group.label}
          </h3>
          <ul className="space-y-1">
            {group.items.map((item) => {
              const Icon = item.icon;
              return (
                <li key={item.label}>
                  <button
                    type="button"
                    onClick={() => router.push(item.href)}
                    className="w-full text-left flex items-start gap-3 px-2.5 py-2 rounded-lg hover:bg-accent transition-colors group"
                  >
                    <span className="w-8 h-8 rounded-md bg-muted text-foreground flex items-center justify-center shrink-0 group-hover:bg-foreground group-hover:text-background transition-colors">
                      <Icon className="w-4 h-4" />
                    </span>
                    <span className="flex flex-col gap-0.5 min-w-0">
                      <span className="text-sm font-semibold text-foreground leading-tight">
                        {item.label}
                      </span>
                      <span className="text-xs text-muted-foreground leading-snug truncate">
                        {item.description}
                      </span>
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        </section>
      ))}
    </div>
  );
}
