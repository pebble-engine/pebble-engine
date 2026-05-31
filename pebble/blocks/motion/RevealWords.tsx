"use client";
import { motion, useReducedMotion } from "framer-motion";

/** Per-word headline reveal. EDIT-SAFE: takes a single plain-string child and
 *  the data-pebble-id rides on the wrapping <span> (via ...rest) — the source
 *  stays one editable string, so click-to-edit text still matches verbatim. */
export default function RevealWords({
  children,
  className,
  ...rest
}: {
  children: string;
  className?: string;
  [k: string]: unknown;
}) {
  const reduce = useReducedMotion();
  const text = typeof children === "string" ? children : "";
  if (reduce) {
    return (
      <span className={className} {...rest}>
        {text}
      </span>
    );
  }
  return (
    <span className={className} {...rest}>
      {text.split(" ").map((w, i) => (
        <motion.span
          key={i}
          className="mr-[0.25em] inline-block"
          initial={{ opacity: 0, y: 24, filter: "blur(6px)" }}
          whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          viewport={{ once: true }}
          transition={{ delay: 0.06 * i, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
        >
          {w}
        </motion.span>
      ))}
    </span>
  );
}
