import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        brand: {
          
          100: "#e0e7ff",
          200: "#c7d2fe",
          300: "#a5b4fc",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
          800: "#3730a3",
          900: "#312e81",
        },
      },
      borderRadius: {
        xl: "0.75rem",
        "2xl": "1rem",
        "3xl": "1.25rem",
      },
      boxShadow: {
        soft: "0 1px 1px rgb(0 0 0 / 0.04), 0 8px 24px rgb(0 0 0 / 0.06)",
        card: "0 1px 0 rgb(0 0 0 / 0.06), 0 10px 30px -10px rgb(2 6 23 / 0.15)",
        ring: "0 0 0 4px rgb(99 102 241 / 0.25)",
      },
      keyframes: {
        "fade-in": { from: { opacity: "0", transform: "translateY(4px)" }, to: { opacity: "1", transform: "translateY(0)" } },
        "pulse-soft": { "0%,100%": { opacity: "0.45" }, "50%": { opacity: "1" } },
      },
      animation: {
        "fade-in": "fade-in .24s ease-out both",
        "pulse-soft": "pulse-soft 1.6s ease-in-out infinite",
      },
    },
  },
  plugins: [],
} satisfies Config;
