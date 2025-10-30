import { create } from "zustand";

type RuntimeAuth = {
  ACCESS_TOKEN_LIFETIME: number;
  JWT_RENEW_AT_SECONDS: number;
  IDLE_TIMEOUT_SECONDS: number;
} | null;

type User = {
  id: number;
  username: string;
  email: string;
  is_staff?: boolean;
  is_superuser?: boolean;
} | null;

type State = {
  runtimeAuth: RuntimeAuth;
  setRuntimeAuth: (r: RuntimeAuth) => void;
  accessToken: string | null;
  refreshToken: string | null;
  user: User;

  setAccessToken: (t: string | null) => void;
  setRefreshToken: (t: string | null) => void;
  setTokens: (access: string, refresh: string) => void;
  applyRefreshedTokens: (access: string, refresh?: string) => void;
  setUser: (u: User) => void;
  logout: () => void;
};

export const useAuthStore = create<State>((set, get) => ({
  runtimeAuth: null,
  setRuntimeAuth: (r) => set({ runtimeAuth: r }),
  accessToken: localStorage.getItem("access"),
  refreshToken: localStorage.getItem("refresh"),
  user: null,

  setAccessToken: (t) => {
    if (t) localStorage.setItem("access", t);
    else localStorage.removeItem("access");
    set({ accessToken: t });
  },

  setRefreshToken: (t) => {
    if (t) localStorage.setItem("refresh", t);
    else localStorage.removeItem("refresh");
    set({ refreshToken: t });
  },

  setTokens: (access, refresh) => {
    localStorage.setItem("access", access);
    localStorage.setItem("refresh", refresh);
    set({ accessToken: access, refreshToken: refresh });
  },

  // Use this after a successful refresh call
  applyRefreshedTokens: (newAccess, newRefresh) => {
    const patch: Partial<State> = { accessToken: newAccess };
    localStorage.setItem("access", newAccess);
    if (newRefresh) {
      patch.refreshToken = newRefresh;
      localStorage.setItem("refresh", newRefresh);
    }
    set(patch);
  },

  setUser: (u) => set({ user: u }),

  logout: () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    set({ accessToken: null, refreshToken: null, user: null });
  },
}));
