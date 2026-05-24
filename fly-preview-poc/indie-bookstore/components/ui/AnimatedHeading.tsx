"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";

type Props = {
  text: string;
  className?: string;
};

export function AnimatedHeading({ text, className }: Props) {
  const isReducedMotion = typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const [skipAnimation, setSkipAnimation] = useState(isReducedMotion);

  useEffect(() => {
    if (isReducedMotion) setSkipAnimation(true);
  }, [isReducedMotion]);

  if (skipAnimation) {
    return <h1 className={className} data-pebble-id="pb-e4dfea">{text}</h1>;
  }

  const lines = text.split("\n");
  return (
    <h1 className={className} aria-hidden="true" data-pebble-id="pb-7de443">
      {lines.map((line, lineIdx) => (
        <div key={lineIdx} className="flex flex-wrap">
          {line.split(" ").map((word, wordIdx) => (
            <span key={wordIdx} className="mr-2 inline-flex" data-pebble-id="pb-070251">
              {word.split("").map((char, charIdx) => (
                <motion.span
                  key={charIdx}
                  initial={{ opacity: 0, y: 40 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: (lineIdx * 10 + charIdx) * 0.05 }}
                  className="inline-block"
                >
                  {char}
                </motion.span>
              ))}
            </span>
          ))}
        </div>
      ))}
      <span className="sr-only" data-pebble-id="pb-d83064">{text}</span>
    </h1>
  );
}