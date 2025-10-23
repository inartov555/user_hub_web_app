import { api } from "../lib/axios";
import { jwtDecode } from "jwt-decode";

export function setupActivityRefresh(thresholdSeconds = 60) {
  const check = async () => {
    const access = localStorage.getItem("access");
    const refresh = localStorage.getItem("refresh");
    if (!access || !refresh) return;

    try {
      const { exp }: { exp: number } = jwtDecode(access);
      const now = Math.floor(Date.now() / 1000);
      if (exp - now <= thresholdSeconds) {
        await api.post("/auth/jwt/refresh/", { refresh }); // will rotate
      }
    } catch { /* ignore */ }
  };

  ["click", "keydown", "mousemove", "scroll", "visibilitychange"].forEach(evt =>
    window.addEventListener(evt, check, { passive: true })
  );
}
