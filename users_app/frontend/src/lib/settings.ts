import { api } from "./axios";

export type AuthSettings = {
  JWT_RENEW_AT_SECONDS: number;
  IDLE_TIMEOUT_SECONDS: number;
  ACCESS_TOKEN_LIFETIME: number;
  ROTATE_REFRESH_TOKENS: boolean;
};

function storeSettingsToLocalStorage(data) {
  // Let's also update the values in localStorage to have the settings accross all pages
  localStorage.setItem("JWT_RENEW_AT_SECONDS", String(Number(data.JWT_RENEW_AT_SECONDS) * 1000)); // in milliseconds
  localStorage.setItem("IDLE_TIMEOUT_SECONDS", String(Number(data.IDLE_TIMEOUT_SECONDS) * 1000)); // in milliseconds
  localStorage.setItem("ACCESS_TOKEN_LIFETIME", data.ACCESS_TOKEN_LIFETIME);
  localStorage.setItem("ROTATE_REFRESH_TOKENS", data.ROTATE_REFRESH_TOKENS);
}

export async function fetchRuntimeAuth() {
  // All users
  const { data } = await api.get("/system/runtime-auth/");
  storeSettingsToLocalStorage(data);
  return data as AuthSettings
}

export async function fetchAuthSettings(): Promise<AuthSettings> {
  // Admin only
  const { data } = await api.get("/system/settings/");
  storeSettingsToLocalStorage(data);
  return data as AuthSettings
}

export async function updateAuthSettings(payload: AuthSettings): Promise<AuthSettings> {
  // Admin only
  const { data } = await api.put("/system/settings/", payload);
  storeSettingsToLocalStorage(data);
  return data as AuthSettings
}
