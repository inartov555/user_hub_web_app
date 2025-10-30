import React from "react";
import { LocaleFlag } from "./LocaleFlag";

type Props = {
  children?: React.ReactNode;
  /** Optional override, e.g. "fi-FI" */
  locale?: string;
  /** Extra classes for sizing/positioning */
  className?: string;
  /** Opacity (0–1) for the background image */
  opacity?: number;
};

export default function LocaleFlagBackground({
  children,
  locale,
  className = "",
  opacity = 0.08,
}: Props) {

  return (
    <div
      className={`relative ${className}`}
      style={{backgroundRepeat: "no-repeat", backgroundPosition: "center", backgroundSize: "contain" }}
    >
      {/* simple overlay to control intensity */}
      <div
        aria-hidden
        style={{
          position: "absolute",
          inset: 0,
          background: "currentColor",
          opacity,
          pointerEvents: "none",
          mixBlendMode: "multiply",
        }}
      />
      <div style={{ position: "relative" }}>{children}</div>
    </div>
  );
}
