import { api } from "../lib/axios";
import { useAuthStore } from "./store";

export async function bootstrapAuth(): Promise<boolean> {
  const { logout } = useAuthStore.getState();

  // If we can't see a token yet (hydration lag), don't probe /me - just bail quietly.
  const inMem = useAuthStore.getState().accessToken;
  const fromLS = localStorage.getItem("access");
  const token = inMem || fromLS;
  if (!token) return false;
  try {
    const { data } = await api.get("/auth/users/me/");
    useAuthStore.getState().setUser(data);
    return true;
  } catch (err: any) {
    const status = err?.response?.status;
    // Only clear tokens for real auth errors. Network/CORS should not log you out.
    if (status === 401 || status === 403) logout?.();
    return false;
  }
}
