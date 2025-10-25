import axios from "axios";
import { AxiosHeaders, InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "../auth/store";
import { jwtDecode } from "jwt-decode";

export const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || "/api",
    withCredentials: false,
    headers: { "Content-Type": "application/json" }
});

let isRefreshing = false;
let pending: Array<(t: string|null)=>void> = [];

function onRefreshed(token: string|null) {
  pending.forEach(cb => cb(token));
  pending = [];
}

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  // Do NOT attach Authorization on JWT endpoints
  const url = (config.url || "").toString();
  const isJwtEndpoint =
    url.includes("/auth/jwt/refresh/") ||
    url.includes("/auth/jwt/create/") ||
    url.includes("/auth/jwt/verify/");

  if (!isJwtEndpoint) {
    const token = useAuthStore.getState().accessToken || localStorage.getItem("access");
    if (token) {
      if (!config.headers) config.headers = new AxiosHeaders();
      if (config.headers instanceof AxiosHeaders && !config.headers?.Authorization) {
        config.headers.set("Authorization", `Bearer ${token}`);
      }
    }
  }

  return config;
});

api.interceptors.response.use(
  r => r,
  async (error) => {
    const { response, config } = error;
    const status = response?.status;

    // If no response (network) or already retried, just bubble up.
    if (!response || (config as any).__isRetry) {
      return Promise.reject(error);
    }

    const url = (config.url || "").toString();

    // Skip handling for auth endpoints (login/refresh/verify) — let callers show errors.
    const isJwtEndpoint =
      url.includes("/auth/jwt/refresh/") ||
      url.includes("/auth/jwt/create/") ||
      url.includes("/auth/jwt/verify/");
    if (isJwtEndpoint) {
      return Promise.reject(error);
    }

    // Some backends return 403 when the token is expired/invalid.
    const isAuthFailure = status === 401 || status === 403;

    if (!isAuthFailure) {
      return Promise.reject(error);
    }

    // Only take over if we *had* tokens; otherwise, let caller handle (public pages).
    const hadAccess = !!(useAuthStore.getState().accessToken || localStorage.getItem("access"));
    const hadRefresh = !!localStorage.getItem("refresh");
    const hadAnyToken = hadAccess || hadRefresh;
    if (!hadAnyToken) {
      return Promise.reject(error);
    }

    // Prevent request stampede while refreshing
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        pending.push((token) => {
          if (!token) return reject(error);
          // Ensure headers are AxiosHeaders and set properly
          if (!config.headers) config.headers = new AxiosHeaders();
          if (config.headers instanceof AxiosHeaders) {
            (config.headers as AxiosHeaders).set("Authorization", `Bearer ${token}`);
          } else {
            // Fallback for odd shapes
            (config.headers as any).Authorization = `Bearer ${token}`;
          }
          (config as any).__isRetry = true;
          resolve(api(config));
        });
      });
    }

    isRefreshing = true;
    try {
      const refresh = localStorage.getItem("refresh");
      if (!refresh) throw new Error("No refresh token");

      // Use a *bare* call to avoid intercept loop side effects;
      // but using `api` is fine since we short-circuit JWT endpoints above.
      const { data } = await api.post("/auth/jwt/refresh/", { refresh });

      const newAccess = data.access as string;
      const newRefresh = data.refresh as string | undefined;

      // Persist tokens
      useAuthStore.getState().setAccessToken(newAccess);
      localStorage.setItem("access", newAccess);
      if (newRefresh) localStorage.setItem("refresh", newRefresh);

      onRefreshed(newAccess);

      // Re-run original request with fresh token
      if (!config.headers) config.headers = new AxiosHeaders();
      if (config.headers instanceof AxiosHeaders) {
        (config.headers as AxiosHeaders).set("Authorization", `Bearer ${newAccess}`);
      } else {
        (config.headers as any).Authorization = `Bearer ${newAccess}`;
      }
      (config as any).__isRetry = true;

      return api(config);
    } catch (e) {
      onRefreshed(null);
      useAuthStore.getState().logout();

      // Only navigate if not already on /login (avoid useless reload loop)
      if (typeof window !== "undefined" && window.location.pathname !== "/login") {
        window.location.assign("/login");
      }

      return Promise.reject(error);
    } finally {
      isRefreshing = false;
    }
  }
);
