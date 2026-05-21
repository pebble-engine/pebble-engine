/**
 * Tiny className concatenator. Filters out falsy values so you can write
 * `cn("base", isActive && "active", maybeUndefined)` without crashes.
 */
export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(" ");
}
