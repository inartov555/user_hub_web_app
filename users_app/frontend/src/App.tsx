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
    <div className="min-h-screen">
      <AppShellHeartbeat />
      <Navbar />
      <main className="max-w-6xl mx-auto p-4">
        <Outlet />
      </main>
      <CookieConsent />
    </div>
  );
}
