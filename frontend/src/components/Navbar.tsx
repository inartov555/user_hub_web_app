import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuthStore } from "../auth/store";
import { useAuth } from "../hooks/useAuth";

export default function Navbar() {
  const { pathname } = useLocation();
  const { user, logout } = useAuthStore();
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  return (
    <header className="sticky top-0 z-10 bg-white/70 backdrop-blur border-b border-slate-200">
      <div className="max-w-6xl mx-auto flex items-center justify-between p-3">
        <Link to="/" className="font-semibold">Users App</Link>
        <nav className="flex gap-4">
          {user && (
            <>
              <Link className={navCls(pathname, "/users")} to="/users">Users</Link>
              <Link className={navCls(pathname, "/stats")} to="/stats">Stats</Link>
              <Link className={navCls(pathname, "/profile")} to="/profile">Profile</Link>
              <Link className={navCls(pathname, "/import-excel")} to="/import-excel">Import from Excel</Link>
            </>
          )}
        </nav>
        <div className="flex items-center gap-3">
          {user ? <span className="text-sm">Hi, {user.username}</span> : <Link to="/login" className="btn">Login</Link>}
          {user && <button className="btn" onClick={() => { logout(); navigate("/login"); }}>Logout</button>}
        </div>
      </div>
    </header>
  );
}

function navCls(path: string, href: string) {
  const active = path.startsWith(href);
  return `px-3 py-1 rounded-lg ${active ? "bg-slate-900 text-white" : "hover:bg-slate-100"}`;
}
