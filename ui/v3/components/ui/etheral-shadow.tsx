"use client";

/**
 * Adapted from 21st.dev's `etheral-shadow` (sic — the source filename
 * has the typo; preserved here so anyone copying the original demo can
 * find this).
 *
 * Animated SVG-filter shadow background — `feTurbulence` +
 * `feDisplacementMap` + a hue-rotate loop on a masked colored shape.
 * Used as the atmospheric background on /landing's hero.
 *
 * Adaptations from the 21st.dev source:
 *  - Removed the hardcoded <h1>"Etheral Shadows"</h1> overlay; the
 *    consumer composes its own foreground text as a sibling.
 *  - Default `color` switched from neutral gray to Pebble river
 *    (#205661) at 0.45 alpha so it reads as atmosphere over the warm
 *    sand background and as a faint cool glow over the dark theme.
 *  - Animation is gated on `prefers-reduced-motion`. When the user
 *    prefers reduced motion, the static masked shape still renders but
 *    the hue-rotate + displacement loop is skipped.
 *  - Renamed export from `Component` to `EtherealShadow` for clarity at
 *    call sites.
 *
 * The mask + noise images live on framerusercontent.com (a stable framer
 * CDN). If we ever want to fully self-host, mirror them into
 * /public/etheral/ and swap the URLs below.
 */

import React, { useRef, useId, useEffect, useState, CSSProperties } from "react";
import {
  animate,
  useMotionValue,
  AnimationPlaybackControls,
  useReducedMotion,
} from "framer-motion";

interface ResponsiveImage {
  src: string;
  alt?: string;
  srcSet?: string;
}

interface AnimationConfig {
  preview?: boolean;
  scale: number;
  speed: number;
}

interface NoiseConfig {
  opacity: number;
  scale: number;
}

interface EtherealShadowProps {
  type?: "preset" | "custom";
  presetIndex?: number;
  customImage?: ResponsiveImage;
  sizing?: "fill" | "stretch";
  color?: string;
  animation?: AnimationConfig;
  noise?: NoiseConfig;
  style?: CSSProperties;
  className?: string;
}

function mapRange(
  value: number,
  fromLow: number,
  fromHigh: number,
  toLow: number,
  toHigh: number,
): number {
  if (fromLow === fromHigh) return toLow;
  const percentage = (value - fromLow) / (fromHigh - fromLow);
  return toLow + percentage * (toHigh - toLow);
}

const useInstanceId = (): string => {
  const id = useId();
  const cleanId = id.replace(/:/g, "");
  return `etheral-${cleanId}`;
};

export function EtherealShadow({
  sizing = "fill",
  color = "rgba(32, 86, 97, 0.45)",
  animation,
  noise,
  style,
  className,
}: EtherealShadowProps) {
  const id = useInstanceId();
  const reducedMotion = useReducedMotion();
  // SSR-safe gate: useReducedMotion() returns null on the server and a
  // boolean on the client. Toggling the SVG filter directly off that
  // signal causes a hydration mismatch (server renders filter, client
  // doesn't, when the user has prefers-reduced-motion enabled). We
  // delay enabling the animation until after mount so server and client
  // first render always agree.
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  const animationEnabled =
    mounted &&
    !reducedMotion &&
    animation !== undefined &&
    animation.scale > 0;
  const feColorMatrixRef = useRef<SVGFEColorMatrixElement>(null);
  const hueRotateMotionValue = useMotionValue(180);
  const hueRotateAnimation = useRef<AnimationPlaybackControls | null>(null);

  const displacementScale = animation
    ? mapRange(animation.scale, 1, 100, 20, 100)
    : 0;
  const animationDuration = animation
    ? mapRange(animation.speed, 1, 100, 1000, 50)
    : 1;

  useEffect(() => {
    if (feColorMatrixRef.current && animationEnabled) {
      if (hueRotateAnimation.current) hueRotateAnimation.current.stop();
      hueRotateMotionValue.set(0);
      hueRotateAnimation.current = animate(hueRotateMotionValue, 360, {
        duration: animationDuration / 25,
        repeat: Infinity,
        repeatType: "loop",
        repeatDelay: 0,
        ease: "linear",
        delay: 0,
        onUpdate: (value: number) => {
          if (feColorMatrixRef.current) {
            feColorMatrixRef.current.setAttribute("values", String(value));
          }
        },
      });

      return () => {
        if (hueRotateAnimation.current) hueRotateAnimation.current.stop();
      };
    }
  }, [animationEnabled, animationDuration, hueRotateMotionValue]);

  return (
    <div
      className={className}
      style={{
        overflow: "hidden",
        position: "relative",
        width: "100%",
        height: "100%",
        ...style,
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: -displacementScale,
          filter: animationEnabled ? `url(#${id}) blur(4px)` : "none",
        }}
      >
        {animationEnabled && animation && (
          <svg style={{ position: "absolute" }}>
            <defs>
              <filter id={id}>
                <feTurbulence
                  result="undulation"
                  numOctaves={2}
                  baseFrequency={`${mapRange(animation.scale, 0, 100, 0.001, 0.0005)},${mapRange(animation.scale, 0, 100, 0.004, 0.002)}`}
                  seed="0"
                  type="turbulence"
                />
                <feColorMatrix
                  ref={feColorMatrixRef}
                  in="undulation"
                  type="hueRotate"
                  values="180"
                />
                <feColorMatrix
                  in="dist"
                  result="circulation"
                  type="matrix"
                  values="4 0 0 0 1  4 0 0 0 1  4 0 0 0 1  1 0 0 0 0"
                />
                <feDisplacementMap
                  in="SourceGraphic"
                  in2="circulation"
                  scale={displacementScale}
                  result="dist"
                />
                <feDisplacementMap
                  in="dist"
                  in2="undulation"
                  scale={displacementScale}
                  result="output"
                />
              </filter>
            </defs>
          </svg>
        )}
        <div
          style={{
            backgroundColor: color,
            maskImage: `url('https://framerusercontent.com/images/ceBGguIpUU8luwByxuQz79t7To.png')`,
            WebkitMaskImage: `url('https://framerusercontent.com/images/ceBGguIpUU8luwByxuQz79t7To.png')`,
            maskSize: sizing === "stretch" ? "100% 100%" : "cover",
            WebkitMaskSize: sizing === "stretch" ? "100% 100%" : "cover",
            maskRepeat: "no-repeat",
            WebkitMaskRepeat: "no-repeat",
            maskPosition: "center",
            WebkitMaskPosition: "center",
            width: "100%",
            height: "100%",
          }}
        />
      </div>

      {noise && noise.opacity > 0 && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            backgroundImage: `url("https://framerusercontent.com/images/g0QcWrxr87K0ufOxIUFBakwYA8.png")`,
            backgroundSize: noise.scale * 200,
            backgroundRepeat: "repeat",
            opacity: noise.opacity / 2,
            pointerEvents: "none",
          }}
        />
      )}
    </div>
  );
}
