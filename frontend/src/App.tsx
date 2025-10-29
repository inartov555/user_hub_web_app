import { useEffect, useState } from "react";
import { Outlet, Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "./auth/store";
import { bootstrapAuth } from "./auth/bootstrap";
import Navbar from "./components/Navbar";

export default function App() {
  const { t, i18n } = useTranslation();
  const { user, accessToken } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();
  const [authReady, setAuthReady] = useState(false);

  useEffect(() => {
    bootstrapAuth().finally(() => setAuthReady(true));
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
