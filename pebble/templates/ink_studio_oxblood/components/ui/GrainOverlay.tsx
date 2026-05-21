/**
 * GrainOverlay — fixed full-screen animated SVG fractalNoise grain.
 * Rendered once in the root layout, sits above bg but below all content via
 * z-index. Disabled automatically via `prefers-reduced-motion` (handled in
 * globals.css; the .grain-overlay class is `display:none` in that media
 * query block).
 */
export function GrainOverlay() {
  return <div className="grain-overlay" aria-hidden="true" />;
}
