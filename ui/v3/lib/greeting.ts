/**
 * greeting.ts — contextual Pebble AI greeting builder.
 *
 * Pure utility — no React, no API calls. All inputs are passed in
 * so the function is trivially testable and SSR-safe.
 *
 * Output format (with project):
 *   "Good morning, Marc! ☀️ Should we keep working on Acme Plumbing?
 *    Remember, quiet progress is still progress."
 *
 * Output format (no projects yet):
 *   "Good morning, Marc! ☀️ Ready to build your first website?
 *    Let's make something amazing together."
 */

// ---------------------------------------------------------------------------
// Content pools
// ---------------------------------------------------------------------------

const MOTIVATIONAL_LINES: string[] = [
  "Remember, quiet progress is still progress.",
  "Every small step forward counts.",
  "You're closer than you think.",
  "Great things are built one day at a time.",
  "Consistency beats perfection every time.",
  "Your best work is just ahead.",
  "Small improvements add up to something remarkable.",
  "The hardest part is starting — you've already done that.",
  "One good session can change everything.",
  "Keep going. It's worth it.",
  "Every revision makes it better.",
  "Progress, not perfection.",
];

/** Project-context prompts — receive the project name and return a
 *  sentence. Vary by hour so returning the same morning feels fresh. */
const PROJECT_PROMPTS: Array<(name: string) => string> = [
  (n) => `Should we keep working on ${n}?`,
  (n) => `Ready to continue where we left off on ${n}?`,
  (n) => `Want to keep building ${n} today?`,
  (n) => `${n} is waiting — shall we pick it up?`,
  (n) => `Shall we make some more progress on ${n}?`,
  (n) => `Let's keep going on ${n} — you've got momentum.`,
];

const NEW_USER_LINES: string[] = [
  "Ready to build your first website? Let's make something amazing together.",
  "Your first website is just one prompt away. Ready to start?",
  "Let's build something great today. What's your idea?",
  "Every great site starts with a single sentence. What's yours?",
];

// ---------------------------------------------------------------------------
// Time-of-day helpers
// ---------------------------------------------------------------------------

type TimeOfDay = "morning" | "afternoon" | "evening";

function getTimeOfDay(hour: number): TimeOfDay {
  if (hour < 12) return "morning";
  if (hour < 18) return "afternoon";
  return "evening";
}

const TIME_ICONS: Record<TimeOfDay, string> = {
  morning:   "☀️",
  afternoon: "🌤️",
  evening:   "🌙",
};

// ---------------------------------------------------------------------------
// Deterministic pick helpers — consistent within a day / hour
// ---------------------------------------------------------------------------

/** Day-of-year (0-indexed). Changes daily so the motivational line
 *  rotates every morning but stays the same all day. */
function dayOfYear(d: Date): number {
  const start = new Date(d.getFullYear(), 0, 0);
  return Math.floor((d.getTime() - start.getTime()) / 86_400_000);
}

function pick<T>(arr: T[], seed: number): T {
  return arr[Math.abs(seed) % arr.length];
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

export interface GreetingOptions {
  /** User's first name. Pass null/undefined for anon/nameless users. */
  firstName?: string | null;
  /** Most recently built project name. Pass null if no projects yet. */
  mostRecentProjectName?: string | null;
  /** Inject a custom Date for deterministic testing. Defaults to now. */
  now?: Date;
}

export function buildGreeting({
  firstName,
  mostRecentProjectName,
  now = new Date(),
}: GreetingOptions): string {
  const hour     = now.getHours();
  const tod      = getTimeOfDay(hour);
  const icon     = TIME_ICONS[tod];
  const day      = dayOfYear(now);

  const salutation = firstName
    ? `Good ${tod}, ${firstName}! ${icon}`
    : `Good ${tod}! ${icon}`;

  if (mostRecentProjectName) {
    const projectLine  = pick(PROJECT_PROMPTS, hour)(mostRecentProjectName);
    const motiveLine   = pick(MOTIVATIONAL_LINES, day);
    return `${salutation} ${projectLine} ${motiveLine}`;
  }

  // New user — no projects yet.
  const newUserLine = pick(NEW_USER_LINES, day);
  return `${salutation} ${newUserLine}`;
}
