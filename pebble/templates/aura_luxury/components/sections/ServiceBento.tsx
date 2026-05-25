"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ShieldCheck,
  HardHat,
  Compass,
  FileCheck,
  X,
  ChevronRight,
  type LucideIcon,
} from "lucide-react";
import { SERVICES, type ServiceItem } from "@/content/site";

const ICON_MAP: Record<string, LucideIcon> = {
  HardHat,
  Compass,
  ShieldCheck,
  FileCheck,
};

export function ServiceBento() {
  const [active, setActive] = useState<ServiceItem | null>(null);

  return (
    <section id="services" className="py-24 px-6 sm:px-12 md:px-20 bg-[#0F1115] relative overflow-hidden border-t border-white/5">
      <div className="absolute top-0 right-0 w-96 h-96 bg-white/[0.01] blur-3xl pointer-events-none" />

      <div className="max-w-7xl mx-auto space-y-16 relative z-10">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-white/5 pb-10">
          <div className="space-y-4">
            <div className="text-[10px] tracking-[0.25em] text-slate-400 uppercase font-sans">
              Service Offerings
            </div>
            <h2 className="text-3xl sm:text-4xl font-serif text-white leading-tight">
              An Elite Protocol <br />
              <span className="italic text-slate-300 font-light">for Every Architecture</span>
            </h2>
          </div>
          <p className="max-w-md text-xs sm:text-sm text-slate-400 font-light leading-relaxed">
            Our cleaning protocols are custom-engineered for specific architectural and operational challenges. We utilize medical-grade technologies and fine material conservation guidelines.
          </p>
        </div>

        <div className="grid grid-cols-12 gap-6 lg:gap-8">
          {SERVICES.map((service) => {
            const Icon = ICON_MAP[service.icon] ?? ShieldCheck;
            const spanClass = service.span === "wide"
              ? "col-span-12 md:col-span-7"
              : "col-span-12 md:col-span-5";
            return (
              <button
                type="button"
                key={service.id}
                onClick={() => setActive(service)}
                className={`${spanClass} text-left cursor-pointer group relative min-h-[340px] rounded-2xl overflow-hidden border border-white/5 bg-[#161920] p-8 md:p-10 flex flex-col justify-between transition-all duration-500`}
              >
                <div className="absolute inset-0 brushed-metal-bg opacity-0 group-hover:opacity-100 transition-opacity duration-500 z-0 pointer-events-none" />
                <div className="absolute top-0 right-0 w-32 h-32 bg-white/[0.02] group-hover:bg-white/[0.04] transition-colors rounded-full blur-2xl z-0 pointer-events-none" />

                <div className="flex justify-between items-start z-10">
                  <div className="p-3 bg-white/5 border border-white/10 rounded-lg group-hover:border-white/20 transition-all duration-300">
                    <Icon className="w-5 h-5 text-white/80 group-hover:text-white transition-colors" />
                  </div>
                  <span className="text-[9px] tracking-[0.2em] text-slate-500 uppercase font-sans mt-1">
                    {service.subtitle}
                  </span>
                </div>

                <div className="z-10 mt-8 space-y-4">
                  <div className="space-y-3 transition-transform duration-300 group-hover:-translate-y-2">
                    <h3 className="text-xl sm:text-2xl font-serif text-white">
                      {service.title}
                    </h3>
                    <p className="text-xs sm:text-sm text-slate-400 font-light leading-relaxed line-clamp-3">
                      {service.description}
                    </p>
                  </div>
                  <div className="overflow-hidden h-6 pt-2">
                    <div className="flex items-center text-[10px] text-white/80 font-sans tracking-[0.15em] uppercase transition-all duration-300 translate-y-2 group-hover:translate-y-0 opacity-0 group-hover:opacity-100">
                      <span>View Specifications</span>
                      <ChevronRight className="w-3.5 h-3.5 ml-1 inline" />
                    </div>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      <AnimatePresence>
        {active && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setActive(null)}
              className="fixed inset-0 bg-black/60 backdrop-blur-md z-50 cursor-zoom-out"
            />
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", damping: 30, stiffness: 200 }}
              className="fixed right-0 top-0 bottom-0 w-full max-w-[460px] bg-[#111319] border-l border-white/10 p-8 sm:p-12 z-50 overflow-y-auto"
            >
              <div className="flex justify-between items-start">
                <div>
                  <span className="text-[10px] tracking-[0.25em] text-slate-400 uppercase font-sans">
                    {active.subtitle}
                  </span>
                  <h3 className="text-2xl sm:text-3xl font-serif text-white mt-1">
                    {active.title}
                  </h3>
                </div>
                <button
                  onClick={() => setActive(null)}
                  aria-label="Close"
                  className="p-2 border border-white/10 rounded-full hover:bg-white/5 transition-colors text-slate-400 hover:text-white"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="mt-8 space-y-6">
                <div>
                  <h4 className="text-[10px] tracking-[0.15em] uppercase text-slate-500 font-sans">Description</h4>
                  <p className="text-sm text-slate-300 font-light leading-relaxed mt-2">
                    {active.description}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4 border-t border-b border-white/5 py-4">
                  <div>
                    <span className="text-[9px] tracking-widest uppercase text-slate-500 font-sans">Average Duration</span>
                    <p className="text-xs font-sans text-white font-medium mt-1">{active.duration}</p>
                  </div>
                  <div>
                    <span className="text-[9px] tracking-widest uppercase text-slate-500 font-sans">Protocol Intensity</span>
                    <p className="text-xs font-sans text-white font-medium mt-1">{active.intensity}</p>
                  </div>
                </div>

                <div className="space-y-3">
                  <h4 className="text-[10px] tracking-[0.15em] uppercase text-slate-500 font-sans">Surgical Specifications</h4>
                  <ul className="space-y-3 pt-1">
                    {active.specs.map((spec, i) => (
                      <li key={i} className="flex items-start text-xs font-sans text-slate-300 leading-normal">
                        <span className="w-1.5 h-1.5 rounded-full bg-white mt-1.5 mr-3 shrink-0" />
                        <span>{spec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </section>
  );
}
