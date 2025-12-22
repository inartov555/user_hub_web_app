import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import Button from "../components/button";

export default function DarkModeToggle() {
  const { t } = useTranslation();
  const [dark, setDark] = useState(
    localStorage.theme === "dark" ||
    (!("theme" in localStorage) && window.matchMedia("(prefers-color-scheme: light)").matches)
  );

  useEffect(() => {
    const root = document.documentElement;
    if (dark) { root.classList.add("dark"); localStorage.theme = "dark"; }
    else { root.classList.remove("dark"); localStorage.theme = "light"; }
  }, [dark]);

  return (
    <Button
      id="lightDarkMode"
      data-tag={dark ? "dark" : "light"}
      className="inline-flex items-center gap-2 rounded-xl px-3 py-2 text-sm shadow-soft"
      onClick={() => setDark(v => !v)}
      aria-label="Toggle dark mode"
    >
      {dark ? <>🌙 {t("lightDarkThemeToggle.dark")}</> : <>☀️ {t("lightDarkThemeToggle.light")}</>}
    </Button>
  );
}
