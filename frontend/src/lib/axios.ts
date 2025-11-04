import axios from "axios";
import { AxiosHeaders, InternalAxiosRequestConfig } from "axios";
import { jwtDecode } from "jwt-decode";
import i18n from "./i18n";
import { useAuthStore } from "../auth/store";

export const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || "/api/v1",
    withCredentials: false,
    headers: { "Content-Type": "application/json" }
});

// Single-flight refresh to avoid concurrent rotation races
let refreshPromise: Promise<{ access: string; refresh?: string }> | null = null;
function startRefresh(): Promise<{ access: string; refresh?: string }> {
  if (refreshPromise) return refreshPromise;
  refreshPromise = (async () => {
    const st = useAuthStore.getState();
    const currentRefresh = st.refreshToken || localStorage.getItem("refresh");
    if (!currentRefresh) throw new Error("No refresh token");
    const { data } = await api.post("/auth/jwt/refresh/", { refresh: currentRefresh }, {
      headers: { "X-Skip-Auth-Checks": "1" }, // ensure interceptor won't loop
    });
    const access = data?.access as string | undefined;
    const refresh = data?.refresh as string | undefined; // may be undefined when rotation OFF
    if (!access) throw new Error("No access token in refresh response");

    // Persist consistently (store + localStorage)
    st.applyRefreshedTokens?.(access, refresh);
    st.setAccessToken?.(access);
    localStorage.setItem("access", access);
    if (refresh) {
      st.setRefreshToken?.(refresh);
      localStorage.setItem("refresh", refresh);
    }
    return { access, refresh };
  })().finally(() => {
    // allow next refresh to start anew
    refreshPromise = null;
  });
  return refreshPromise;
}

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  config.headers = AxiosHeaders.from(config.headers || {});
  const headers = config.headers as AxiosHeaders;
  const uiLang = (i18n?.language || navigator.language || "en-US").toLowerCase().replace("_", "-");
  headers.set("Accept-Language", uiLang);
  headers.set("X-Locale", uiLang);
  return config;
});

api.interceptors.request.use(async (config) => {
  // allow explicitly skipping client-side checks for bootstrap calls
  const skip = (config.headers as any)?.["X-Skip-Auth-Checks"];
  if (skip) {
    const { accessToken } = useAuthStore.getState();
    const headers = AxiosHeaders.from(config.headers || {});
    if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
    headers.delete("X-Skip-Auth-Checks");
    config.headers = headers;
    return config;
  }

  const {
    accessToken,
    refreshToken,
    accessExpiresAt,
    runtimeAuth, // has JWT_RENEW_AT_SECONDS, IDLE_TIMEOUT_SECONDS, etc.
  } = useAuthStore.getState();

  // PROACTIVE REFRESH: compare against JWT exp
  if (
    accessToken &&
    accessExpiresAt &&
    refreshToken &&
    runtimeAuth?.JWT_RENEW_AT_SECONDS > 0 &&
    runtimeAuth.ROTATE_REFRESH_TOKENS
  ) {
    // Renew token only if runtimeAuth.ROTATE_REFRESH_TOKENS is true
    const remainingMs = accessExpiresAt - Date.now();
    const renewWindowMs = (runtimeAuth.JWT_RENEW_AT_SECONDS || 0);
    if (remainingMs <= renewWindowMs) {
      try {
        const { access, refresh } = await startRefresh();
        // headers will be set below from store/localStorage
      } catch {
        // Do NOT logout here - let the request go and the response 401 handler decide
      }
    }
  }

  // attach Authorization with the latest token (survives reloads via localStorage)
  const latestAccess = useAuthStore.getState().accessToken || localStorage.getItem("access");
  if (latestAccess) {
    const headers = AxiosHeaders.from(config.headers || {});
    headers.set("Authorization", `Bearer ${latestAccess}`);
    config.headers = headers;
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

    // Only take over if there are tokens; otherwise, let caller handle (public pages).
    const hadAccess = !!(useAuthStore.getState().accessToken || localStorage.getItem("access"));
    const hadRefresh = !!localStorage.getItem("refresh");
    const hadAnyToken = hadAccess || hadRefresh;
    if (!hadAnyToken || !hadRefresh) {
      return Promise.reject(error);
    }
    try {
      const { access: newAccess } = await startRefresh();

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
      useAuthStore.getState().logout();

      // Only navigate if not already on /login (avoid useless reload loop)
      if (typeof window !== "undefined" && window.location.pathname !== "/login") {
        window.location.assign("/login");
      }

      return Promise.reject(error);
    } finally {
      // nothing to do
    }
  }
);
