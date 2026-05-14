"use client";
export function AnimatedHeading({ text }: { text: string }) {
  return (
    <h1 style={{ textShadow: "0 2px 24px rgba(0,0,0,0.5)" }}>
      <span className="sr-only">{text}</span>
      <span aria-hidden="true">{text}</span>
    </h1>
  );
}
