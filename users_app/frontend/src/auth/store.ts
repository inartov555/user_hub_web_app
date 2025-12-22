import { create } from "zustand";
import { jwtDecode } from "jwt-decode";

type JwtPayload = { exp?: number };

const decodeAccessExp = (jwt: string | null): number | null => {
  if (!jwt) return null;
  try {
    const { exp } = jwtDecode<JwtPayload>(jwt); // reliable exp
    return typeof exp === "number" ? exp * 1000 : null;
  } catch {
    return null;
  }
};

/**
 * Runtime auth settings are stored in localStorage by fetchRuntimeAuth().
 * NOTE: despite the *_SECONDS key names, the frontend stores these values in milliseconds.
 *
 * Returning null here is important: a { IDLE_TIMEOUT_SECONDS: 0, ... } object is truthy
 */
const readRuntimeAuthFromLocalStorage = (): RuntimeAuth => {
  try {
    const renewRaw = localStorage.getItem("JWT_RENEW_AT_SECONDS");
    const idleRaw = localStorage.getItem("IDLE_TIMEOUT_SECONDS");
    const lifetimeRaw = localStorage.getItem("ACCESS_TOKEN_LIFETIME");
    const rotateRaw = localStorage.getItem("ROTATE_REFRESH_TOKENS");

    const anyPresent =
      renewRaw !== null || idleRaw !== null || lifetimeRaw !== null || rotateRaw !== null;
    if (!anyPresent) return null;

    const toFiniteOrZero = (v: string | null): number => {
      if (v === null) return 0;
      const n = Number(v);
      return Number.isFinite(n) ? n : 0;
    };

    return {
      JWT_RENEW_AT_SECONDS: toFiniteOrZero(renewRaw),
      IDLE_TIMEOUT_SECONDS: toFiniteOrZero(idleRaw),
      ACCESS_TOKEN_LIFETIME: toFiniteOrZero(lifetimeRaw),
      ROTATE_REFRESH_TOKENS: rotateRaw === "true" || rotateRaw === "1",
    };
  } catch {
    return null;
  }
};

type RuntimeAuth = {
  JWT_RENEW_AT_SECONDS: number;
  IDLE_TIMEOUT_SECONDS: number;
  ACCESS_TOKEN_LIFETIME: number;
  ROTATE_REFRESH_TOKENS: boolean;
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
  setRuntimeAuth: () => void;
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
  runtimeAuth: readRuntimeAuthFromLocalStorage(),
    setRuntimeAuth: () => {
    const now = Date.now();
    const rt = readRuntimeAuthFromLocalStorage();
    set({ runtimeAuth: rt, lastActivityAt: now });

    // ensure we don't stack multiple watchers
    get().stopIdleWatch();
    if (rt && rt.IDLE_TIMEOUT_SECONDS > 0) get().startIdleWatch();
  },
  accessToken: localStorage.getItem("access"),
  refreshToken: localStorage.getItem("refresh"),
  accessExpiresAt: decodeAccessExp(localStorage.getItem("access")),
  user: null,

  lastActivityAt: Date.now(),
  idleTimer: null,
  setActivityNow: () => set({ lastActivityAt: Date.now() }),

  startIdleWatch: () => {
    const rt = get().runtimeAuth;
    if (!rt || !(rt.IDLE_TIMEOUT_SECONDS > 0)) return;

    get().stopIdleWatch();

    const onActivity = get().setActivityNow;
    ["mousemove","keydown","click","touchstart","visibilitychange","focus"].forEach(evt =>
      window.addEventListener(evt, onActivity, { passive: true })
    );

    const tick = () => {
      const rt = get().runtimeAuth;
      if (!rt || !(rt.IDLE_TIMEOUT_SECONDS > 0)) return; // <- guard

      const idleFor = Date.now() - get().lastActivityAt;
      if (idleFor >= rt.IDLE_TIMEOUT_SECONDS) {
        get().logout();
        get().stopIdleWatch();
      } else {
        // schedule next check precisely at the remaining time (min 1s)
        const remaining = rt.IDLE_TIMEOUT_SECONDS - idleFor;
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

  setTokens: (access: string, refresh?: string) => {
    get().setAccessToken(access);
    // only update refresh if a value was provided; otherwise leave it unchanged
    if (typeof refresh !== "undefined") {
      get().setRefreshToken(refresh);
    }
    set({
      lastActivityAt: Date.now(), // nice to stamp activity
    });
  },

  // Use this after a successful refresh call
  applyRefreshedTokens: (access: string, refresh?: string) => {
    // rotate refresh if backend returned one
    get().setAccessToken(access);
    // only update refresh if a value was provided; otherwise leave it unchanged
    if (typeof refresh !== "undefined") {
      get().setRefreshToken(refresh);
    }
    set({
      lastActivityAt: Date.now(),
    });
  },

  setUser: (u) => set({ user: u }),

  logout: () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    set({ accessToken: null, refreshToken: null, accessExpiresAt: null, user: null });
  },
}));
