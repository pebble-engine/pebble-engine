"use client";

import { useRef, useState } from "react";
import Image from "next/image";
import {
  BEFORE_AFTER_TITLE,
  BEFORE_AFTER_PILL,
  BEFORE_AFTER_BODY,
  BEFORE_IMAGE,
  AFTER_IMAGE,
} from "@/content/site";

export function BeforeAfter() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [percent, setPercent] = useState(50);
  const [dragging, setDragging] = useState(false);

  const handleMove = (clientX: number) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = clientX - rect.left;
    setPercent(Math.max(0, Math.min(100, (x / rect.width) * 100)));
  };

  return (
    <section id="comparisons" className="py-20 px-6 bg-[#1e293b]">
      <div className="max-w-5xl mx-auto">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div className="space-y-4">
            <span className="text-[#facc15] uppercase text-xs tracking-[0.2em] font-bold">
              {BEFORE_AFTER_PILL}
            </span>
            <h2 className="font-[family-name:var(--font-display)] text-4xl text-[#fafaf9] uppercase">
              {BEFORE_AFTER_TITLE}
            </h2>
            <p className="text-[#e7e5e4]/60 text-sm leading-relaxed">{BEFORE_AFTER_BODY}</p>
          </div>
          <div
            ref={containerRef}
            onPointerDown={(e) => {
              setDragging(true);
              handleMove(e.clientX);
              e.currentTarget.setPointerCapture(e.pointerId);
            }}
            onPointerUp={(e) => {
              setDragging(false);
              e.currentTarget.releasePointerCapture(e.pointerId);
            }}
            onPointerMove={(e) => {
              if (dragging || e.pointerType === "mouse") handleMove(e.clientX);
            }}
            className="relative w-full aspect-video overflow-hidden border-4 border-[#e7e5e4]/50 bg-[#e7e5e4] cursor-ew-resize select-none"
          >
            {/* After (full) */}
            <Image
              src={AFTER_IMAGE}
              alt="After repair"
              fill
              sizes="(max-width: 768px) 100vw, 50vw"
              className="object-cover pointer-events-none"
            />
            {/* Before (clipped from right) */}
            <div
              className="absolute inset-0 z-10 overflow-hidden pointer-events-none"
              style={{ clipPath: `inset(0 ${100 - percent}% 0 0)` }}
            >
              <Image
                src={BEFORE_IMAGE}
                alt="Before repair"
                fill
                sizes="(max-width: 768px) 100vw, 50vw"
                className="object-cover pointer-events-none grayscale"
              />
            </div>
            {/* Labels */}
            <span className="absolute top-3 left-3 z-20 text-[10px] px-2 py-0.5 bg-[#1e293b] text-[#facc15] uppercase tracking-wide font-bold pointer-events-none">
              BEFORE
            </span>
            <span className="absolute top-3 right-3 z-20 text-[10px] px-2 py-0.5 bg-[#1e293b] text-[#facc15] uppercase tracking-wide font-bold pointer-events-none">
              AFTER
            </span>
            {/* Handle */}
            <div
              className="absolute top-0 bottom-0 w-1 bg-[#facc15] z-30 pointer-events-none flex items-center justify-center"
              style={{ left: `${percent}%`, transform: "translateX(-50%)", boxShadow: "0 0 10px rgba(0,0,0,0.3)" }}
            >
              <div className="w-8 h-8 rounded-full bg-[#1e293b] border-2 border-[#facc15] text-[#facc15] flex items-center justify-center font-mono text-sm font-bold">
                ↔
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
