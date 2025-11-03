import { api } from "../lib/axios";
import { useAuthStore } from "./store";

export async function bootstrapAuth(): Promise<boolean> {
  const { setUser, setTokens, logout } = useAuthStore.getState();
  // Hydrate tokens from storage FIRST
  const access = localStorage.getItem("access");
  const refresh = localStorage.getItem("refresh");
  if (!access || !refresh) {
    // nothing to bootstrap
    return false;
  }
  setTokens?.(access, refresh);

  // Validate with the server; request interceptor will include Authorization
  try {
    const { data } = await api.get("/auth/users/me/");
    setUser?.(data);
    return true;
  } catch {
    // tokens invalid/expired
    logout?.();
    return false;
  }
}
