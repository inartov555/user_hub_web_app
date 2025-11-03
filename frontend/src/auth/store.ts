import { create } from "zustand";
import { jwtDecode } from "jwt-decode";

type JwtPayload = { exp?: number };

const decodeAccessExp = (jwt: string | null): number | null => {
  if (!jwt) return null;
  try {
    const { exp } = jwtDecode<JwtPayload>(jwt);   // ✅ reliable exp
    return typeof exp === "number" ? exp * 1000 : null;
  } catch {
    return null;
  }
};

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
  accessExpiresAt: number | null;
  lastActivityAt: number;
  idleTimer?: number | null;
  setActivityNow: () => void;
  startIdleWatch: () => void;
  stopIdleWatch: () => void;
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
  setRuntimeAuth: (r) => {
    const now = Date.now();
    set({ runtimeAuth: r, lastActivityAt: now });
    if (r && r.IDLE_TIMEOUT_SECONDS > 0) {
      get().startIdleWatch();
    } else {
      get().stopIdleWatch();
    }
  },
  accessToken: localStorage.getItem("access"),
  refreshToken: localStorage.getItem("refresh"),
  accessExpiresAt: decodeAccessExp(localStorage.getItem("access")),
  user: null,

  lastActivityAt: Date.now(),
  idleTimer: null,
  setActivityNow: () => set({ lastActivityAt: Date.now() }),

  startIdleWatch: () => {
    const onActivity = () => get().setActivityNow();
    ["mousemove","keydown","click","touchstart","visibilitychange","focus"].forEach(evt =>
      window.addEventListener(evt, onActivity, { passive: true })
    );

    const tick = () => {
      const rt = get().runtimeAuth;
      if (!rt || !(rt.IDLE_TIMEOUT_SECONDS > 0)) return; // <- guard

      const idleFor = Date.now() - get().lastActivityAt;
      if (idleFor >= rt.IDLE_TIMEOUT_SECONDS * 1000) {
        get().logout();
        get().stopIdleWatch();
      } else {
        // schedule next check precisely at the remaining time (min 1s)
        const remaining = rt.IDLE_TIMEOUT_SECONDS * 1000 - idleFor;
        const id = window.setTimeout(tick, Math.max(remaining, 1000));
        set({ idleTimer: id });
      }
    };

    // kick off
    const id = window.setTimeout(tick, 1000);
    set({ idleTimer: id });
  },

  stopIdleWatch: () => {
    const id = get().idleTimer;
    if (id) clearTimeout(id);
    ["mousemove","keydown","click","touchstart","visibilitychange","focus"].forEach(evt =>
      window.removeEventListener(evt, get().setActivityNow as any)
    );
    set({ idleTimer: null });
  },

  setAccessToken: (t) => {
    if (t) localStorage.setItem("access", t);
    else localStorage.removeItem("access");
    set({ accessToken: t, accessExpiresAt: decodeAccessExp(t) });
  },

  setRefreshToken: (t) => {
    if (t) localStorage.setItem("refresh", t);
    else localStorage.removeItem("refresh");
    set({ refreshToken: t });
  },

  setTokens: (access: string, refresh?: string) => set((state) => ({
    accessToken: access,
    refreshToken: refresh ?? state.refreshToken,
    accessExpiresAt: decodeAccessExp(access),
    lastActivityAt: Date.now(), // nice to stamp activity
  })),

  // Use this after a successful refresh call
  applyRefreshedTokens: (access: string, refresh?: string) => set((state) => ({
    accessToken: access,
    // rotate refresh if backend returned one
    ...(refresh ? { refreshToken: refresh } : {}),
    accessExpiresAt: decodeAccessExp(access),
    lastActivityAt: Date.now(),
  })),

  setUser: (u) => set({ user: u }),

  logout: () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    set({ accessToken: null, refreshToken: null, accessExpiresAt: null, user: null });
  },
}));
