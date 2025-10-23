import { api } from "../lib/axios";
import { useAuthStore } from "./store";

export async function bootstrapAuth(): Promise<boolean> {
  const { user, setUser, logout } = useAuthStore.getState();

  // Do we have tokens saved from a previous login?
  const access = localStorage.getItem("access");
  const refresh = localStorage.getItem("refresh");
  if (!access || !refresh) return false;

  // If user already in memory, we're good.
  if (user) return true;

  // Ask backend who we are. If access is expired, your axios refresh
  // interceptor should kick in automatically.
  try {
    const { data } = await api.get("/auth/users/me/");
    setUser(data);
    return true;
  } catch {
    logout(); // tokens invalid → clear them
    return false;
  }
}
