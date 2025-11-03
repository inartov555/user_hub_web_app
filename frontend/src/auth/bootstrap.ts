import { api } from "../lib/axios";
import { useAuthStore } from "./store";

export async function bootstrapAuth(): Promise<boolean> {
  const { setUser, logout, setTokens } = useAuthStore.getState();

  const access = localStorage.getItem("access");
  const refresh = localStorage.getItem("refresh");
  if (!access) return false;

  setTokens?.(access, refresh || undefined);

  try {
    const { data } = await api.get("/auth/users/me/", {
      headers: { "X-Skip-Auth-Checks": "1" },
    });
    setUser(data);
    return true;
  } catch (err: any) {
    const s = err?.response?.status;
    if (s === 401 || s === 403) logout?.();
    return false;
  }
}
