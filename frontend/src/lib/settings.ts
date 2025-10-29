import { api } from "../axios";

export type AuthSettings = {
  JWT_RENEW_AT_SECONDS: number;
  IDLE_TIMEOUT_SECONDS: number;
  ACCESS_TOKEN_LIFETIME: number;
};

export async function fetchAuthSettings(): Promise<AuthSettings> {
  const { data } = await api.get("/system/settings/");
  return data;
}

export async function updateAuthSettings(payload: AuthSettings): Promise<AuthSettings> {
  const { data } = await api.put("/system/settings/", payload);
  return data;
}
