import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useEffect, useState, useMemo } from "react";
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
  const { user, accessToken, logout } = useAuthStore();
  const location = useLocation();
  const [ready, setReady] = useState(false);

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

  return (
    <>
      <Outlet />
      {shouldRedirect && <Navigate to="/login" replace state={{ from: location }} />}
    </>
  );
}
