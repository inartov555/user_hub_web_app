import { api } from "../lib/axios";
import { useAuthStore } from "./store";
import { extractApiError } from "../lib/httpErrors";

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
  } catch (erro: any) {
    const parsed = extractApiError(erro);
    console.log("bootstrap catch; parsed = ", parsed)
    logout?.(); // tokens invalid/expired — clear them
    return true;
  }
}
