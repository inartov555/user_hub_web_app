import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";
import { jwtDecode } from "jwt-decode";
import { useAuthStore } from "./store";
import { bootstrapAuth } from "./bootstrap";

export default function ProtectedRoute() {
  const location = useLocation();

  const isAuthRoute = useMemo(() => {
    const p = location.pathname;
    return p === "/login" || p === "/signup" || p.startsWith("/reset-password");
  }, [location.pathname]);

  const user = useAuthStore((s) => s.user);
  const accessToken = useAuthStore((s) => s.accessToken);

  // Consider storage tokens on first paint so we don't misclassify the session
  const hasTokens = useMemo(() => {
    return !!accessToken ||
           !!localStorage.getItem("access") ||
           !!localStorage.getItem("refresh");
  }, [accessToken]);

  // One-shot bootstrap if we see any token
  const [bootstrapping, setBootstrapping] = useState<boolean>(hasTokens && !user);
  useEffect(() => {
    let cancelled = false;
    (async () => {
      if (!hasTokens || user) {
        if (!cancelled) setBootstrapping(false);
        return;
      }
      try {
        await bootstrapAuth(); // populates user if token is valid
      } finally {
        if (!cancelled) setBootstrapping(false);
      }
    })();
    return () => { cancelled = true; };
  }, [hasTokens, user]);

  // Do NOT call logout here based on local exp checks. Let axios handle refresh/401.

  const shouldRedirect = !isAuthRoute && !bootstrapping && !user && !hasTokens;

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
