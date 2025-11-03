import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useEffect, useState, useMemo } from "react";
import { useTranslation } from "react-i18next";
import { jwtDecode } from "jwt-decode";
import { useAuthStore } from "./store";
import { bootstrapAuth } from "./bootstrap";

function isExpired(t?: string | null) {
  if (!t) return true;
  try {
    const { exp } = jwtDecode<{ exp: number }>(t);
    return !exp || Date.now() >= exp * 1000;
  } catch {
    return true;
  }
}

export default function ProtectedRoute() {
  const { t, i18n } = useTranslation();
  const { user, accessToken, logout } = useAuthStore();
  const location = useLocation();
  const [ready, setReady] = useState(false);
  const [checking, setChecking] = useState(true);
  const [allowed, setAllowed] = useState(false);

  useEffect(() => {
    let alive = true;

    (async () => {
      // Fast path: if we already have a user in store, allow.
      if (user) {
        if (alive) { setAllowed(true); setChecking(false); }
        return;
      }

      // Otherwise, try to bootstrap from persisted tokens.
      const ok = await bootstrapAuth().catch(() => false);
      if (!alive) return;

      setAllowed(!!ok);
      setChecking(false);
    })();

    return () => { alive = false; };
  }, [user]);


  // Treat these as public routes where we never render a redirect to /login
  const isAuthRoute = useMemo(() => {
    const p = location.pathname;
    return p === "/login" || p === "/signup" || p === "/reset-password";
  }, [location.pathname]);

  // Proactive local check: if token clearly expired, clear state
  useEffect(() => {
    if (!isAuthRoute && isExpired(accessToken)) {
      logout();
    }
  }, [isAuthRoute, accessToken, logout]);

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

  // While not ready, never decide to redirect — just render children.
  if (!ready) {
    return <Outlet />;
  }

  // Decide redirect only after validation finished and never from auth pages
  const hasTokens = !!(accessToken || localStorage.getItem("access"));
  const shouldRedirect = !isAuthRoute && !user && !hasTokens;

  // Save intended page for post-login redirect
  if (shouldRedirect) {
    const intended = location.pathname + location.search + location.hash;
    localStorage.setItem("postLoginRedirect", intended);
  }

  /*
  // While deciding, render nothing (or a skeleton) so children don't fire requests.
  if (checking) return <div className="p-4">{t("users.loading")}</div>;
  if (!allowed) {
    localStorage.setItem("postLoginRedirect", location.pathname + location.search + location.hash);
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  */

  if (!allowed) {
    // remember intended path for after login
    const intended = location.pathname + location.search + location.hash;
    localStorage.setItem("postLoginRedirect", intended);
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}
