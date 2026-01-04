import { useEffect, useState } from "react";
import { Outlet, Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "./lib/axios";
import { useAuthStore } from "./auth/store";
import { bootstrapAuth } from "./auth/bootstrap";
import Navbar from "./components/Navbar";
import CookieConsent from "./components/CookieConsent";

function AppShellHeartbeat() {
  useEffect(() => {
    let timer: number | null = null;

    const tick = async () => {
      const { runtimeAuth, accessToken } = useAuthStore.getState();

    if (accessToken && document.visibilityState === "visible") {
      try {
        await api.get("/auth/users/me/", { headers: { "X-Skip-Auth-Checks": "1" } });
      } catch {
        // ignore; response interceptor handles auth failures
      }
    }

    const configured = runtimeAuth?.IDLE_TIMEOUT_SECONDS;
    const periodMs =
      Number.isFinite(configured) && (configured as number) > 0
        ? (configured as number)
        : 60000;

    timer = window.setTimeout(tick, periodMs);
    };

    tick();
    return () => { if (timer) window.clearTimeout(timer); };
  }, []);

  return null;
}

export default function App() {
  const { t, i18n } = useTranslation();
  const { user, accessToken } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();
  const [authReady, setAuthReady] = useState(false);

  useEffect(() => {
    bootstrapAuth().finally(() => setAuthReady(true));
    useAuthStore.getState().setRuntimeAuth();
    return () => useAuthStore.getState().stopIdleWatch();
  }, []);

  useEffect(() => {
    if (!authReady) return;
    const hasTokens = !!(accessToken || localStorage.getItem("access"));
    // Public routes that should be reachable without auth
    const isPublic =
      location.pathname === "/login" ||
      location.pathname === "/signup" ||
      location.pathname.startsWith("/reset-password");

    if (!user && !hasTokens && !isPublic) {
      navigate("/login", { replace: true, state: { from: location } });
    }
  }, [authReady, user, accessToken, location, navigate]);

  if (!authReady) {
    // Prevent a flash-redirect to /login before hydration completes
    return <div className="p-4">{t("users.loading")}</div>;
  }

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Background */}
      <div aria-hidden className="pointer-events-none absolute inset-0">
        {/* base gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-100 via-slate-50/70 to-indigo-50/60 dark:from-slate-950 dark:via-slate-900/80 dark:to-indigo-950/80" />

        {/* soft blobs */}
        <div className="absolute -top-32 -left-32 h-[520px] w-[520px] rounded-full bg-indigo-300/20 blur-3xl dark:bg-indigo-500/10" />
        <div className="absolute -bottom-40 -right-40 h-[560px] w-[560px] rounded-full bg-fuchsia-300/16 blur-3xl dark:bg-fuchsia-500/08" />
        <div className="absolute top-1/3 left-1/2 h-[420px] w-[420px] -translate-x-1/2 rounded-full bg-sky-300/14 blur-3xl dark:bg-sky-500/08" />

        {/* subtle grid */}
        <div
          className="absolute inset-0 opacity-[0.05] dark:opacity-[0.04]
          [background-image:radial-gradient(circle_at_1px_1px,currentColor_1px,transparent_0)]
          [background-size:18px_18px] text-slate-900 dark:text-white"
        />

        {/* vignette */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-slate-900/6 dark:to-black/20" />
      </div>

      {/* Content */}
      <div className="relative z-10 min-h-screen">
        <AppShellHeartbeat />
        <Navbar />
        <main className="max-w-6xl mx-auto p-4">
          <Outlet />
        </main>
        <CookieConsent />
      </div>
    </div>
  );
}
