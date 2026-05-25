"use client";

import React, { useRef, useState } from "react";
import Image from "next/image";
import { Sparkles, ArrowLeftRight } from "lucide-react";
import {
  TRANSFORM_IMAGE,
  TRANSFORM_PILL,
  TRANSFORM_TITLE,
  TRANSFORM_BODY,
  TRANSFORM_BEFORE_LABEL,
  TRANSFORM_AFTER_LABEL,
  TRANSFORM_STATS,
} from "@/content/site";

export function TransformationSlider() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [percent, setPercent] = useState(50);

  const handleMove = (clientX: number) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = clientX - rect.left;
    const next = Math.max(0, Math.min(100, (x / rect.width) * 100));
    setPercent(next);
  };

  const handlePointerDown = (e: React.PointerEvent) => {
    setIsDragging(true);
    handleMove(e.clientX);
    e.currentTarget.setPointerCapture(e.pointerId);
  };

  const handlePointerUp = (e: React.PointerEvent) => {
    setIsDragging(false);
    e.currentTarget.releasePointerCapture(e.pointerId);
  };

  const handlePointerMove = (e: React.PointerEvent) => {
    if (isDragging || e.pointerType === "mouse") {
      handleMove(e.clientX);
    }
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (e.touches.length > 0) handleMove(e.touches[0].clientX);
  };

  return (
    <section id="transformation" className="py-24 px-6 sm:px-12 md:px-20 bg-[#1a1410] relative overflow-hidden border-t border-white/5">
      <div className="max-w-7xl mx-auto space-y-16">
        <div className="text-center space-y-4 max-w-2xl mx-auto">
          <div className="inline-flex items-center space-x-2 text-[10px] tracking-[0.25em] text-slate-400 uppercase font-sans border border-white/10 px-3 py-1.5 rounded-full bg-white/5">
            <Sparkles className="w-3.5 h-3.5 text-white/80" />
            <span>{TRANSFORM_PILL}</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-serif text-white leading-tight">
            {TRANSFORM_TITLE}
          </h2>
          <p className="text-xs sm:text-sm text-slate-400 font-light leading-relaxed tracking-wide">
            {TRANSFORM_BODY}
          </p>
        </div>

        <div
          ref={containerRef}
          onPointerDown={handlePointerDown}
          onPointerMove={handlePointerMove}
          onPointerUp={handlePointerUp}
          onTouchMove={handleTouchMove}
          className="relative w-full h-[400px] sm:h-[500px] lg:h-[600px] rounded-2xl overflow-hidden border border-white/10 shadow-[0_20px_60px_rgba(0,0,0,0.6)] select-none cursor-ew-resize"
        >
          {/* After (bottom layer) */}
          <div className="absolute inset-0 z-0">
            <Image
              src={TRANSFORM_IMAGE}
              alt="Pristine cleaned luxury kitchen"
              fill
              sizes="100vw"
              className="object-cover pointer-events-none filter saturate-[1.1] contrast-[1.05]"
            />
            <div className="absolute left-6 top-6 bg-black/60 backdrop-blur-md border border-white/10 rounded-md px-3 py-1.5 z-10 pointer-events-none">
              <span className="text-[10px] font-sans tracking-widest text-white uppercase font-medium">{TRANSFORM_AFTER_LABEL}</span>
            </div>
          </div>

          {/* Before (clipped) */}
          <div
            className="absolute inset-0 z-10 overflow-hidden pointer-events-none"
            style={{
              clipPath: `inset(0 0 0 ${percent}%)`,
              WebkitClipPath: `inset(0 0 0 ${percent}%)`,
            }}
          >
            <Image
              src={TRANSFORM_IMAGE}
              alt="Dull uncleaned kitchen before protocol"
              fill
              sizes="100vw"
              className="object-cover pointer-events-none filter grayscale contrast-[0.8] brightness-[0.6] blur-[0.7px]"
            />
            <div className="absolute right-6 top-6 bg-black/60 backdrop-blur-md border border-white/10 rounded-md px-3 py-1.5 z-10 pointer-events-none">
              <span className="text-[10px] font-sans tracking-widest text-slate-400 uppercase font-medium">{TRANSFORM_BEFORE_LABEL}</span>
            </div>
          </div>

          {/* Slider handle */}
          <div
            className="absolute top-0 bottom-0 z-20 w-0.5 bg-white/40 backdrop-blur-sm pointer-events-none"
            style={{ left: `${percent}%` }}
          >
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-black/75 border border-white/20 backdrop-blur-md flex items-center justify-center text-white shadow-2xl">
              <ArrowLeftRight className="w-4 h-4 text-white/90" />
            </div>
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-2.5 h-2.5 rounded-full bg-white/60" />
            <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-2.5 h-2.5 rounded-full bg-white/60" />
          </div>

          <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-20 pointer-events-none">
            <div className="bg-black/50 backdrop-blur-sm border border-white/5 rounded-full px-4 py-2 text-[10px] tracking-widest uppercase font-sans text-slate-300 shadow-xl flex items-center space-x-2">
              <span className="inline-block w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
              <span>Hover or Drag to Compare Precision</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8 pt-8 border-t border-white/5 max-w-5xl mx-auto">
          {TRANSFORM_STATS.map((stat) => (
            <div key={stat.label} className="space-y-1">
              <div className="text-[10px] font-sans tracking-widest uppercase text-slate-500">{stat.label}</div>
              <div className="text-xl font-serif text-white">{stat.value}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
