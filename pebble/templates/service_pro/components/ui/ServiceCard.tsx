import Link from "next/link";
import type { Service } from "@/content/site";
import { cn } from "@/lib/cn";

const ICONS: Record<string, React.ReactNode> = {
  leaf: <LeafIcon />,
  home: <HomeIcon />,
  building: <BuildingIcon />,
  shield: <ShieldIcon />,
  bug: <BugIcon />,
  paw: <PawIcon />,
};

export function ServiceCard({ service, className }: { service: Service; className?: string }) {
  const icon = ICONS[service.icon] ?? ICONS.shield;
  return (
    <Link
      href={`/services#${service.id}`}
      className={cn(
        "group glass-card relative flex flex-col gap-4 rounded-2xl p-6 sm:p-7",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-bg",
        className,
      )}
    >
      <span className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/15 text-primary">
        {icon}
      </span>
      <div className="space-y-2">
        <h3 className="font-display text-xl font-semibold tracking-tight text-fg">{service.name}</h3>
        <p className="text-sm text-muted">{service.description}</p>
      </div>
      <span className="mt-auto inline-flex items-center gap-1.5 text-sm font-medium text-primary">
        Learn more
        <ArrowIcon className="transition-transform group-hover:translate-x-1" />
      </span>
    </Link>
  );
}

function ArrowIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M5 12h14M13 5l7 7-7 7" />
    </svg>
  );
}

function LeafIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19.2 2.5c1 1.5.5 7-2 9.5-2.5 2.5-6 2.7-8.2 1m0 0L5 22" />
    </svg>
  );
}
function HomeIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M3 9.5 12 3l9 6.5V21a1 1 0 0 1-1 1h-5v-7h-6v7H4a1 1 0 0 1-1-1V9.5z" />
    </svg>
  );
}
function BuildingIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="4" y="2" width="16" height="20" rx="2" />
      <path d="M9 22v-4h6v4M8 6h.01M16 6h.01M8 10h.01M16 10h.01M8 14h.01M16 14h.01" />
    </svg>
  );
}
function ShieldIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  );
}
function BugIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M8 2 9.5 4M16 2l-1.5 2M8 11h8M8 14h8M19 6c-1.7 1.7-3 4-3 6 0 4-2 6-4 6s-4-2-4-6c0-2-1.3-4.3-3-6M2 12h2M20 12h2M5 19l2-1M19 19l-2-1" />
    </svg>
  );
}
function PawIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="11" cy="4.5" r="2" />
      <circle cx="18.5" cy="8" r="2" />
      <circle cx="3.5" cy="8" r="2" />
      <circle cx="6.5" cy="15.5" r="2" />
      <circle cx="15.5" cy="15.5" r="2" />
      <path d="M11 14c-2 0-3 1-3 2.5 0 1.5.5 3 3 3s3-1.5 3-3c0-1.5-1-2.5-3-2.5z" />
    </svg>
  );
}
