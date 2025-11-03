import { jwtDecode } from "jwt-decode";
import { api } from "../lib/axios";
import { useAuthStore } from "../auth/store";

type JwtPayload = { exp?: number };

export function preloadAuthFromStorage() {
  const access = localStorage.getItem("access");
  const refresh = localStorage.getItem("refresh");

  if (access && !api.defaults.headers.common["Authorization"]) {
    api.defaults.headers.common["Authorization"] = `Bearer ${access}`;
  }

  // Prime the store if available
  try {
    let accessExpiresAt: number | null = null;
    if (access) {
      try {
        const { exp } = jwtDecode<JwtPayload>(access);
        accessExpiresAt = exp ? exp * 1000 : null;
      } catch {
        accessExpiresAt = null;
      }
    }
    useAuthStore.setState({
      accessToken: access || null,
      refreshToken: refresh || null,
      accessExpiresAt,
    });
  } catch {
    // store may not be initialized yet; safe to ignore
  }
}
