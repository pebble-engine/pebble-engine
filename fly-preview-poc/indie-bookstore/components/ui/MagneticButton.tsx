"use client";
import { useState, useRef, ReactNode } from "react";
import { motion, useSpring } from "framer-motion";

type Props = {
  children: ReactNode;
  href?: string;
  onClick?: () => void;
  className?: string;
};

export function MagneticButton({ children, href, onClick, className }: Props) {
  const ref = useRef<HTMLButtonElement>(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });

  const spring = useSpring(position, { damping: 25, stiffness: 150, rest: 0 });

  const handleMouseMove = (e: React.MouseEvent) => {
    const el = ref.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    setPosition({ x, y });
  };

  const handleMouseLeave = () => {
    setPosition({ x: 0, y: 0 });
  };

  const el = (
    <motion.button
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{ x: spring.x, y: spring.y }}
      className={className}
      onClick={onClick}
    >
      {children}
    </motion.button>
  );

  return href ? <a href={href} data-pebble-id="pb-e32feb">{el}</a> : el;
}