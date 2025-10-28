// LocaleFlag.tsx
import React from "react";
import CountryFlag from "react-country-flag";
import { localeToCountry } from "./localeToCountry";

type Props = {
  locale: string;               // e.g., "en-US", "et-EE", "fr"
  size?: number;                // px, both width/height; default 20
  squared?: boolean;            // if you want square corners instead of round
  className?: string;
  title?: string;               // a11y/title override
  svg?: boolean;                // use SVG (crisper) instead of emoji
};

export const LocaleFlag: React.FC<Props> = ({
  locale,
  size = 20,
  squared = false,
  className,
  title,
  svg = true,
}) => {
  const cc = localeToCountry(locale);
  return (
    <CountryFlag
      countryCode={cc}
      svg={svg}
      aria-label={title ?? cc}
      title={title ?? locale}
      className={className}
      style={{
        width: size,
        height: size,
        lineHeight: `${size}px`,
        borderRadius: squared ? 4 : size / 2,
        display: "inline-block",
        objectFit: "cover",
      }}
    />
  );
};
