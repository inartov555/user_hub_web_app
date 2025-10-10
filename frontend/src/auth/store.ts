import { create } from "zustand";

type State = {
  accessToken: string | null;
  refreshToken: string | null;
  user: { id: number; username: string; email: string } | null;
  setTokens: (access: string, refresh: string) => void;
  setUser: (u: any) => void;
  logout: () => void;
};

export const useAuthStore = create<State>((set) => ({
  accessToken: localStorage.getItem("access") || null,
  refreshToken: localStorage.getItem("refresh") || null,
  user: null,
  setTokens: (access, refresh) => {
    localStorage.setItem("access", access);
    localStorage.setItem("refresh", refresh);
    set({ accessToken: access, refreshToken: refresh });
  },
  setUser: (u) => set({ user: u }),
  logout: () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    set({ accessToken: null, refreshToken: null, user: null });
  },
}));
