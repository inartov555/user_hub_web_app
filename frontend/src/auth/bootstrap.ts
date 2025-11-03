import { api } from "../lib/axios";
import { useAuthStore } from "./store";

export async function bootstrapAuth(): Promise<boolean> {
  const { setUser, logout, setTokens } = useAuthStore.getState();

  // Read whatever we have; do NOT require refresh to exist
  const access = localStorage.getItem("access");
  const refresh = localStorage.getItem("refresh");

  if (!access) {
    return false;
  }
  // Prime the store so axios can pick it up immediately
  setTokens?.(access, refresh || undefined);

  try {
    // Mark this call as a bootstrap probe, so client-side auth checks won't interfere
    const { data } = await api.get("/auth/users/me/", {
      headers: { "X-Skip-Auth-Checks": "1" },
    });
    setUser(data);
    return true;
  } catch (err: any) {
    const status = err?.response?.status;
    // Only clear tokens on genuine auth failures
    if (status === 401 || status === 403) {
      logout?.();
    }
    return false;
  }
}
