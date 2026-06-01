"use client";
import type { ReactNode } from "react";

/** CSS-column masonry gallery layout. Layout-only — wrap each image in <FadeUp>
 *  for per-item reveal so each image keeps its own data-pebble-id/src. */
export default function Masonry({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className={`columns-2 gap-4 md:columns-3 [&>*]:mb-4 ${className ?? ""}`}>
      {children}
    </div>
  );
}
