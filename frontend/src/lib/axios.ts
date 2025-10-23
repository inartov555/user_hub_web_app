import axios from "axios";
import { AxiosHeaders, InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "../auth/store";
import { jwtDecode } from "jwt-decode";

export const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || "/api",
    withCredentials: true,
    headers: { "Content-Type": "application/json" }
});

let isRefreshing = false;
let pending: Array<(t: string|null)=>void> = [];

function onRefreshed(token: string|null) {
  pending.forEach(cb => cb(token));
  pending = [];
}

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().accessToken || localStorage.getItem("access");
  if (token) {
    if (!config.headers) config.headers = new AxiosHeaders();
    if (config.headers instanceof AxiosHeaders && !config.headers?.Authorization) {
      config.headers.set("Authorization", `Bearer ${token}`);
    }
  }
  return config;
});

api.interceptors.response.use(
  r => r,
  async (error) => {
    const { response, config } = error;
    if (!response || response.status !== 401 || config.__isRetry) {
      return Promise.reject(error);
    }

    // prevent stampede
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        pending.push((token) => {
          if (!token) return reject(error);
          config.headers.Authorization = `Bearer ${token}`;
          config.__isRetry = true;
          resolve(api(config));
        });
      });
    }

    isRefreshing = true;
    try {
      const refresh = localStorage.getItem("refresh");
      if (!refresh) throw new Error("No refresh token");

      const { data } = await api.post("/auth/jwt/refresh/", { refresh });
      const newAccess = data.access as string;
      const newRefresh = data.refresh as string | undefined;

      // store tokens
      useAuthStore.getState().setAccessToken(newAccess);
      localStorage.setItem("access", newAccess);
      if (newRefresh) {
        localStorage.setItem("refresh", newRefresh); // rotation!
      }

      onRefreshed(newAccess);
      config.headers.Authorization = `Bearer ${newAccess}`;
      config.__isRetry = true;
      return api(config);
    } catch (e) {
      onRefreshed(null);
      useAuthStore.getState().logout(); // clears tokens + redirects
      return Promise.reject(error);
    } finally {
      isRefreshing = false;
    }
  }
);
