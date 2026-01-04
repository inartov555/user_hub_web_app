interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
/* */
/*
// IMPORTANT: if you run via Docker Compose, "localhost:8000" is wrong from inside the frontend container.
// Use the Compose service name (likely "backend") so it reaches Django in the other container.
const BACKEND = process.env.VITE_BACKEND_URL || "http://backend:8000";

export default defineConfig({
  plugins: [react()],
  base: "/",
  server: {
    proxy: {
      "/api/v1": { target: "http://localhost:8000", changeOrigin: true },
    },
  },
});
*/

// Vitest configuration
export const test = {
  environment: "jsdom",
  setupFiles: ["./src/test/setup.ts"],
  globals: true,
};
