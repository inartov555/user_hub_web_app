import { useEffect, useState } from "react";
import Button from "../components/button";

export default function DarkModeToggle() {
  const [dark, setDark] = useState(
    localStorage.theme === "dark" ||
    (!("theme" in localStorage) && window.matchMedia("(prefers-color-scheme: dark)").matches)
  );

  useEffect(() => {
    const root = document.documentElement;
    if (dark) { root.classList.add("dark"); localStorage.theme = "dark"; }
    else { root.classList.remove("dark"); localStorage.theme = "light"; }
  }, [dark]);

  return (
    <Button
      className="inline-flex items-center gap-2 rounded-xl px-3 py-2 text-sm border border-slate-200 bg-white hover:bg-slate-50 shadow-soft"
      onClick={() => setDark(v => !v)}
      aria-label="Toggle dark mode"
    >
      {dark ? "🌙 Dark" : "☀️ Light"}
    </Button>
  );
}
