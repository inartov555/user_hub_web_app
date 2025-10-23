import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { useAuthStore } from "./store";
import { bootstrapAuth } from "./bootstrap";

export default function ProtectedRoute() {
  const { user, accessToken } = useAuthStore();
  const location = useLocation();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    bootstrapAuth().finally(() => setReady(true));
  }, []);

  const hasTokens = !!(accessToken || localStorage.getItem("access"));
  const mustRedirect = ready && !user && !hasTokens;
  useEffect(() => {
    if (mustRedirect) {
      const intended = location.pathname + location.search + location.hash;
      localStorage.setItem("postLoginRedirect", intended);
    }
  }, [mustRedirect, location.pathname, location.search, location.hash]);

  if (!ready) return null; // or a tiny spinner

  return (
    <>
      {/* Keep mounted to avoid input focus loss */}
      <Outlet />
      {mustRedirect && <Navigate to="/login" replace state={{ from: location }} />}
    </>
  );
}
