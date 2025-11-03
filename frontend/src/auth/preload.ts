import { jwtDecode } from "jwt-decode";
import { api } from "../lib/axios";
import { useAuthStore } from "../auth/store";

type JwtPayload = { exp?: number };

export function preloadAuthFromStorage() {
  const access = localStorage.getItem("access");
  const refresh = localStorage.getItem("refresh");

  // 1) Set default Authorization so the FIRST request after reload is authenticated
  if (access && !api.defaults.headers.common["Authorization"]) {
    api.defaults.headers.common["Authorization"] = `Bearer ${access}`;
  }

  // 2) Prime your store (if you have one). If you don't, this is harmless.
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
    // store not available or different shape — ignore
  }
}
