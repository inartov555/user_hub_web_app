import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// IMPORTANT: if you run via Docker Compose, "localhost:8000" is wrong from inside the frontend container.
// Use the Compose service name (likely "backend") so it reaches Django in the other container.
// const BACKEND = process.env.VITE_BACKEND_URL || "http://backend:8000";

export default defineConfig({
  plugins: [react()],
  base: "/", // crucial for correct asset paths behind nginx/django
  appType: "spa",
  server: {
    port: 5173,
    strictPort: true,
    // Only proxy API. Do NOT proxy "/" or "*"
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
});
