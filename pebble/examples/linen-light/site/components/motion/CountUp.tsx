"use client";
import { useEffect, useRef, useState } from "react";
import { useInView, useReducedMotion, animate } from "framer-motion";

/** Animated number that counts up when scrolled into view. EDIT-SAFE: takes a
 *  single numeric/string child; renders the final number as plain text. */
export default function CountUp({
  children,
  className,
  suffix = "",
  ...rest
}: {
  children: number | string;
  className?: string;
  suffix?: string;
  [k: string]: unknown;
}) {
  const to =
    typeof children === "number"
      ? children
      : parseInt(String(children).replace(/\D/g, ""), 10) || 0;
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true });
  const reduce = useReducedMotion();
  const [val, setVal] = useState(0);
  useEffect(() => {
    if (!inView) return;
    if (reduce) {
      setVal(to);
      return;
    }
    const controls = animate(0, to, {
      duration: 1.6,
      ease: "easeOut",
      onUpdate: (v) => setVal(Math.round(v)),
    });
    return () => controls.stop();
  }, [inView, to, reduce]);
  return (
    <span ref={ref} className={className} {...rest}>
      {val.toLocaleString()}
      {suffix}
    </span>
  );
}
