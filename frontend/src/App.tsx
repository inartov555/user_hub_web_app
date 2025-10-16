import { useEffect } from "react";
import { Outlet, Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuthStore } from "./auth/store";
import Navbar from "./components/Navbar";

export default function App() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();
  useEffect(() => {
    if (!user && location.pathname !== "/login") {
      navigate("/login", { replace: true, state: { from: location } });
    }
  }, [user, location, navigate]);
  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="max-w-6xl mx-auto p-4">
        <Outlet />
      </main>
      {!user && (
	<div className="fixed bottom-4 right-4 card">
	  <p className="mb-2">Use a superuser (create in Django admin) to log in.</p>
	  <Link to="/login" className="btn">Login</Link>
        </div>
      )}
    </div>
  );
}
