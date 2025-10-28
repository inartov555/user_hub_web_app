// src/components/LocaleFlag.tsx
import React from "react";
import CountryFlag from "react-country-flag";

type Props = {
  locale: string; // STRICT: "ll-rr" e.g., "en-us", "et-ee"
  size?: number;
  squared?: boolean;
  className?: string;
  title?: string;
  svg?: boolean;
};

const LOCALE_RE = /^[a-z]{2}-[a-z]{2}$/;
const REGION_ALIASES: Record<string, string> = {
  en: "us", // English (US)
  et: "ee", // Estonian
};

function normalizeStrictLocale(locale: string): string {
  const norm = String(locale || "").replace(/_/g, "-").toLowerCase().trim();
  if (!LOCALE_RE.test(norm)) {
    throw new Error(
      `Locale must be in "ll-rr" format (e.g., "en-us", "et-ee"). Got: "${locale}".`
    );
  }
  return norm;
}

function countryFromStrictLocale(locale: string): string {
  const [_, regionRaw] = normalizeStrictLocale(locale).split("-");
  const region = regionRaw.toLowerCase();
  const iso2 = (REGION_ALIASES[region] ?? region).toUpperCase(); // e.g., "us", "ee" -> "US", "EE"
  return iso2;
}

export const LocaleFlag: React.FC<Props> = ({
  locale,
  size = 20,
  squared = false,
  className,
  title,
  svg = true,
}) => {
  let countryCode = "US";
  try {
    countryCode = countryFromStrictLocale(locale);
  } catch (e) {
    // Nothing to do, for now
  }

  return (
    <CountryFlag
      countryCode={countryCode}
      svg={svg}
      aria-label={title ?? countryCode}
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
