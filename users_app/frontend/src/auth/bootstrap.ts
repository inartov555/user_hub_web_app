import { api } from "../lib/axios";
import { useAuthStore } from "./store";

export async function bootstrapAuth(): Promise<boolean> {
  const { setUser, logout, setTokens } = useAuthStore.getState();

  // Require both tokens to even try
  const access = localStorage.getItem("access");
  const refresh = localStorage.getItem("refresh");
  if (!access || !refresh) return false;
  setTokens?.(access, refresh);
  // Always validate with the server. If access is expired, the axios
  // interceptor will attempt a refresh; if refresh is also expired,
  // it will logout and we return false.
  try {
    const { data } = await api.get("/auth/users/me/");
    setUser(data); // keep user store in sync
    return true;
  } catch {
    logout?.(); // tokens invalid/expired — clear them
    return false;
  }
}
