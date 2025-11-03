import { useEffect, useState } from "react";
import { Outlet, Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "./auth/store";
import { bootstrapAuth } from "./auth/bootstrap";
import Navbar from "./components/Navbar";
import { fetchRuntimeAuth, api } from "./lib/axios";

export function AppShellHeartbeat() {
  useEffect(() => {
    let timer: number | null = null;

    const tick = async () => {
      const { runtimeAuth, accessToken } = useAuthStore.getState();
      if (!runtimeAuth || !accessToken) {
        // nothing to keep alive
      } else if (document.visibilityState === "visible") {
        try {
          await api.get("/auth/users/me/", { headers: { "X-Skip-Auth-Checks": "1" } });
          // any authorized endpoint works; /auth/ping is fine if you have it
        } catch {
          // ignore; response interceptor will handle auth failures globally
        }
      }
      const periodMs = Math.max(15000, Math.min(60000, runtimeAuth ? runtimeAuth.IDLE_TIMEOUT_SECONDS * 500 : 30000));
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
  const [ready, setReady] = useState(false);

  // Server validation: run on route changes and when tab regains focus
  useEffect(() => {
    let aborted = false;
    const run = async () => {
      setReady(false);
      try {
        await bootstrapAuth();
      } finally {
        if (!aborted) setReady(true);
      }
    };
    run();
    const onFocusOrVisible = () => {
      if (document.visibilityState === "visible") run();
    };
    window.addEventListener("focus", onFocusOrVisible);
    document.addEventListener("visibilitychange", onFocusOrVisible);
    return () => {
      aborted = true;
      window.removeEventListener("focus", onFocusOrVisible);
      document.removeEventListener("visibilitychange", onFocusOrVisible);
    };
  }, [location.pathname, location.search, location.hash]);

  useEffect(() => {
    bootstrapAuth().finally(() => setAuthReady(true));
    useAuthStore.getState().startIdleWatch();
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
      console.log("user = ", user)
      console.log("hasTokens = ", hasTokens)
      console.log("isPublic = ", isPublic)
      // navigate("/login", { replace: true, state: { from: location } });
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
      {!user && (
        // Add a new component, if needed
        <div></div>
      )}
    </div>
  );
}
