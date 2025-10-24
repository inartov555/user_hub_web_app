import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { useAuthStore } from "./store";
import { bootstrapAuth } from "./bootstrap";

export default function ProtectedRoute() {
  const { user, accessToken } = useAuthStore();
  const location = useLocation();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setReady(false);
    bootstrapAuth().finally(() => setReady(true));
  }, [location.pathname, location.search, location.hash]);

  // Also revalidate when the tab regains focus or visibility changes
  useEffect(() => {
    const recheck = () => {
      setReady(false);
      bootstrapAuth().finally(() => setReady(true));
    };
    window.addEventListener("focus", recheck);
    window.addEventListener("visibilitychange", recheck);
    return () => {
      window.removeEventListener("focus", recheck);
      window.removeEventListener("visibilitychange", recheck);
    };
  }, []);

  const hasTokens = !!(accessToken || localStorage.getItem("access"));
  const mustRedirect = ready && !user && !hasTokens;

  useEffect(() => {
    if (mustRedirect) {
      const intended = location.pathname + location.search + location.hash;
      localStorage.setItem("postLoginRedirect", intended);
    }
  }, [mustRedirect, location.pathname, location.search, location.hash]);

  // This line may affect rendering, e.g. some input elements cannot be filled with data
  // if (!ready) return null; // or a tiny spinner

  return (
    <>
      {/* Keep mounted to avoid input focus loss */}
      <Outlet />
      {mustRedirect && <Navigate to="/login" replace state={{ from: location }} />}
    </>
  );
}
