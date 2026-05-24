"use client";
import { useEffect } from "react";
import Lenis from "lenis";
import { initScrollAnimations } from "@/lib/motion";

export function SmoothScroll({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t: number) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
      syncTouch: true,
      touchMultiplier: 2,
      infinite: false,
    });

    function raf(time: number) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);

    initScrollAnimations();

    return () => {
      lenis.destroy();
    };
  }, []);

  return children;
}