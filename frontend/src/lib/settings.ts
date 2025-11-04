import { api } from "./axios";

export type AuthSettings = {
  JWT_RENEW_AT_SECONDS: number;
  IDLE_TIMEOUT_SECONDS: number;
  ACCESS_TOKEN_LIFETIME: number;
  ROTATE_REFRESH_TOKENS: boolean;
};

export async function fetchRuntimeAuth() {
  // All users
  const { data } = await api.get("/system/runtime-auth/");
  // Let's also update the values in localStorage to have the settings accross all pages
  localStorage.setItem("JWT_RENEW_AT_SECONDS", data.JWT_RENEW_AT_SECONDS);
  localStorage.setItem("IDLE_TIMEOUT_SECONDS", data.IDLE_TIMEOUT_SECONDS);
  localStorage.setItem("ACCESS_TOKEN_LIFETIME", data.ACCESS_TOKEN_LIFETIME);
  localStorage.setItem("ROTATE_REFRESH_TOKENS", data.ROTATE_REFRESH_TOKENS);
  return data as AuthSettings
}

export async function fetchAuthSettings(): Promise<AuthSettings> {
  // Admin only
  const { data } = await api.get("/system/settings/");
  // Updating values in localStorage is not needed here since updates are made in fetchRuntimeAuth() while logging in
  return data as AuthSettings
}

export async function updateAuthSettings(payload: AuthSettings): Promise<AuthSettings> {
  // Admin only
  const { data } = await api.put("/system/settings/", payload);
  // Let's also update the values in localStorage to have the settings accross all pages
  localStorage.setItem("JWT_RENEW_AT_SECONDS", data.JWT_RENEW_AT_SECONDS);
  localStorage.setItem("IDLE_TIMEOUT_SECONDS", data.IDLE_TIMEOUT_SECONDS);
  localStorage.setItem("ACCESS_TOKEN_LIFETIME", data.ACCESS_TOKEN_LIFETIME);
  localStorage.setItem("ROTATE_REFRESH_TOKENS", data.ROTATE_REFRESH_TOKENS);
  return data as AuthSettings
}
