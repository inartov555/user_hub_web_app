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

  if (!ready) return null; // or a tiny spinner

  const hasTokens = !!(accessToken || localStorage.getItem("access"));
  const mustRedirect = ready && !user && !hasTokens;
  if (mustRedirect) {
    // remember where we tried to go
    const intended = location.pathname + location.search + location.hash;
    localStorage.setItem("postLoginRedirect", intended);
    return <Navigate to="/login" replace state={{ from: location }} />;
  }, [mustRedirect, location]);

  return (
    <>
      {/* Always mounted → prevents focus loss */}
      <Outlet />
      {/* When we truly know we're unauthenticated, navigate away */}
      {mustRedirect && <Navigate to="/login" replace state={{ from: location }} />}
    </>
  );
}
