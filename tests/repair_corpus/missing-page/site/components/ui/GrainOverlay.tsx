"use client";
export function GrainOverlay() {
  return (
    <div className="fixed inset-0 pointer-events-none z-50"
      style={{ mixBlendMode: "overlay", opacity: 0.03 }} aria-hidden="true">
      <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
        <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.65" /></filter>
        <rect width="100%" height="100%" filter="url(#grain)" />
      </svg>
    </div>
  );
}
