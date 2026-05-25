"use client";

import React, { useRef, useState } from "react";
import Image from "next/image";
import { motion, useSpring } from "framer-motion";
import { Sparkles, Shield, Maximize2, ArrowRight } from "lucide-react";
import {
  HERO_IMAGE,
  HERO_PILL,
  HERO_HEADLINE_1,
  HERO_HEADLINE_2,
  HERO_HEADLINE_3,
  HERO_BODY,
  HERO_CTA,
  HERO_CTA_HREF,
  SPECS,
  PILLARS,
} from "@/content/site";

const ICON_MAP: Record<string, React.ComponentType<{ className?: string }>> = {
  Sparkles,
  Shield,
  Maximize: Maximize2,
};

const BUBBLES = [
  { x: 80,  y: 100, size: 24, opacity: 0.7 },
  { x: 420, y: 120, size: 36, opacity: 0.5 },
  { x: 380, y: 480, size: 20, opacity: 0.6 },
  { x: 60,  y: 420, size: 28, opacity: 0.8 },
  { x: 110, y: 520, size: 16, opacity: 0.4 },
  { x: 450, y: 340, size: 40, opacity: 0.6 },
  { x: 310, y: 80,  size: 18, opacity: 0.5 },
  { x: 160, y: 260, size: 22, opacity: 0.7 },
  { x: 320, y: 380, size: 30, opacity: 0.5 },
  { x: 250, y: 500, size: 24, opacity: 0.6 },
];

export function Hero() {
  const containerRef = useRef<HTMLDivElement>(null);
  const rotateX = useSpring(0, { stiffness: 90, damping: 20 });
  const rotateY = useSpring(0, { stiffness: 90, damping: 20 });

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const xVal = e.clientX - rect.left;
    const yVal = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    rotateX.set((centerY - yVal) / 25);
    rotateY.set((xVal - centerX) / 25);
  };

  const handleMouseLeave = () => {
    rotateX.set(0);
    rotateY.set(0);
  };

  return (
    <section className="relative min-h-[90vh] flex items-center justify-center py-20 px-6 sm:px-12 md:px-20 overflow-hidden bg-[#0f1612]">
      {/* Editorial Decorative Background Pattern */}
      <div className="absolute inset-0 pointer-events-none opacity-20">
        <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] rounded-full bg-white/[0.01] blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-[600px] h-[600px] rounded-full bg-white/[0.01] blur-3xl" />
        <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:64px_64px]" />
      </div>

      <div className="max-w-7xl w-full grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center relative z-10">
        {/* Left column */}
        <div className="lg:col-span-6 flex flex-col space-y-8 select-none">
          <div className="inline-flex items-center space-x-2 text-[10px] tracking-[0.25em] text-slate-400 uppercase font-sans border border-white/10 px-3 py-1.5 rounded-full w-fit bg-white/5">
            <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
            <span>{HERO_PILL}</span>
          </div>

          <div className="space-y-4">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-serif font-light leading-[1.15] text-white tracking-tight">
              {HERO_HEADLINE_1} <br />
              <span className="font-normal italic text-slate-300">{HERO_HEADLINE_2}</span> <br />
              {HERO_HEADLINE_3}
            </h1>
            <p className="max-w-md text-sm sm:text-base text-slate-400 font-sans font-light leading-relaxed tracking-wide pt-2">
              {HERO_BODY}
            </p>
          </div>

          <div className="pt-4">
            <a
              href={HERO_CTA_HREF}
              className="inline-flex items-center group space-x-4 text-xs tracking-[0.2em] uppercase font-sans text-white border-b border-white/20 pb-2 hover:border-white transition-colors duration-300"
            >
              <span>{HERO_CTA}</span>
              <motion.span
                animate={{ x: [0, 4, 0] }}
                transition={{ repeat: Infinity, duration: 1.5, ease: "easeInOut" }}
              >
                <ArrowRight className="w-4 h-4" />
              </motion.span>
            </a>
          </div>

          <div className="grid grid-cols-3 gap-6 pt-12 border-t border-white/5 max-w-lg">
            {PILLARS.map((p) => {
              const Icon = ICON_MAP[p.icon] ?? Sparkles;
              return (
                <div key={p.title} className="flex flex-col space-y-2">
                  <Icon className="w-5 h-5 text-white/70" />
                  <span className="text-[11px] font-sans tracking-widest text-slate-300 uppercase">{p.title}</span>
                  <span className="text-[10px] font-sans text-slate-500">{p.body}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right column: parallax showcase */}
        <div className="lg:col-span-6 flex justify-center">
          <div
            ref={containerRef}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
            className="w-full max-w-[500px] h-[600px] relative rounded-2xl cursor-crosshair overflow-visible group"
            style={{ perspective: 1200 }}
          >
            <motion.div
              style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
              className="w-full h-full relative"
            >
              {/* Background image */}
              <motion.div
                style={{ translateZ: -80 }}
                className="absolute inset-0 rounded-2xl overflow-hidden border border-white/10 shadow-[0_30px_100px_rgba(0,0,0,0.8)] filter grayscale contrast-[1.1] brightness-[0.7]"
              >
                <Image
                  src={HERO_IMAGE}
                  alt="Monochrome luxury penthouse interior"
                  fill
                  priority
                  sizes="(max-width: 768px) 100vw, 500px"
                  className="object-cover transition-transform duration-700 group-hover:scale-105"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#0f1612] via-transparent to-transparent opacity-90" />
              </motion.div>

              {/* Spec checklist */}
              <motion.div
                style={{ translateZ: 60 }}
                className="absolute right-[-20px] top-[15%] w-[280px] backdrop-blur-xl bg-black/40 border border-white/10 rounded-xl p-5 shadow-[0_20px_50px_rgba(0,0,0,0.5)] select-none pointer-events-none"
              >
                <div className="mb-4">
                  <div className="text-[10px] font-sans tracking-[0.2em] text-slate-400 uppercase">Sanitization Spec</div>
                  <div className="text-sm font-serif font-light text-white mt-1">Surgical Clean Checklist</div>
                </div>
                <div className="space-y-3">
                  {SPECS.map((spec) => (
                    <div key={spec.label} className="flex justify-between items-center text-[11px] font-sans border-b border-white/5 pb-1.5">
                      <span className="text-slate-400 font-light">{spec.label}</span>
                      <span className="text-white font-medium tracking-wide">{spec.value}</span>
                    </div>
                  ))}
                </div>
              </motion.div>

              {/* Floating bubbles (simplified — no cursor repel) */}
              <div className="absolute inset-0 pointer-events-none overflow-visible">
                {BUBBLES.map((b, i) => (
                  <motion.div
                    key={i}
                    initial={{ y: 0 }}
                    animate={{ y: [0, -8, 0] }}
                    transition={{ repeat: Infinity, duration: 3 + (i % 3), ease: "easeInOut", delay: i * 0.2 }}
                    style={{
                      position: "absolute",
                      left: b.x,
                      top: b.y,
                      width: b.size,
                      height: b.size,
                      opacity: b.opacity,
                    }}
                    className="rounded-full bg-gradient-to-tr from-white/20 to-white/5 border border-white/30 backdrop-blur-[1px] shadow-[0_0_15px_rgba(255,255,255,0.15)]"
                  />
                ))}
              </div>

              {/* Active sterility index chip */}
              <motion.div
                style={{ translateZ: 100 }}
                className="absolute left-6 bottom-6 flex flex-col space-y-1 bg-white/5 backdrop-blur-sm border border-white/10 rounded px-3 py-1.5 pointer-events-none"
              >
                <span className="text-[9px] font-sans tracking-widest text-slate-400 uppercase">Active Sterility Index</span>
                <span className="text-xs font-serif font-medium text-white">99.997% Particulate-Free</span>
              </motion.div>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}
