import { api } from "./axios";

export type AuthSettings = {
  JWT_RENEW_AT_SECONDS: number;
  IDLE_TIMEOUT_SECONDS: number;
  ACCESS_TOKEN_LIFETIME: number;
};

export async function fetchRuntimeAuth() {
  // All users
  const { data } = await api.get("/system/runtime-auth/");
  localStorage.setItem("JWT_RENEW_AT_SECONDS", data.JWT_RENEW_AT_SECONDS);
  localStorage.setItem("IDLE_TIMEOUT_SECONDS", data.IDLE_TIMEOUT_SECONDS);
  localStorage.setItem("ACCESS_TOKEN_LIFETIME", data.ACCESS_TOKEN_LIFETIME);
  return data as AuthSettings
}

export async function fetchAuthSettings(): Promise<AuthSettings> {
  // Admin only
  const { data } = await api.get("/system/settings/");
  return data as AuthSettings
}

export async function updateAuthSettings(payload: AuthSettings): Promise<AuthSettings> {
  // Admin only
  const { data } = await api.put("/system/settings/", payload);
  localStorage.setItem("JWT_RENEW_AT_SECONDS", data.JWT_RENEW_AT_SECONDS);
  localStorage.setItem("IDLE_TIMEOUT_SECONDS", data.IDLE_TIMEOUT_SECONDS);
  localStorage.setItem("ACCESS_TOKEN_LIFETIME", data.ACCESS_TOKEN_LIFETIME);
  return data as AuthSettings
}
