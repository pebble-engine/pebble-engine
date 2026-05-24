"use client";
import { useRef } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

export function Parallax({ children, speed = 0.5 }: { children: React.ReactNode; speed?: number }) {
  const sectionRef = useRef<HTMLElement>(null);
  const innerRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    if (!innerRef.current) return;
    gsap.to(innerRef.current, {
      yPercent: -20 * speed,
      ease: "none",
      scrollTrigger: {
        trigger: sectionRef.current,
        start: "top bottom",
        end: "bottom top",
        scrub: 1,
      },
    });
  }, { scope: sectionRef });

  return (
    <section ref={sectionRef} className="relative overflow-hidden">
      <div ref={innerRef} className="relative z-10">
        {children}
      </div>
    </section>
  );
}