import { Link, useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../auth/store";

export default function Navbar() {
  const { pathname } = useLocation();
  const { user, logout, accessToken } = useAuthStore();
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  return (
    <header className="sticky top-0 z-10 bg-white/70 backdrop-blur border-b border-slate-200">
      <div className="max-w-6xl mx-auto flex items-center justify-between p-3">
        <Link to="/" className="font-semibold">{t("app.title")}</Link>
        <nav className="flex gap-4">
          {user && (
            <>
              <Link className={navCls(pathname, "/users")} to="/users">{t("nav.users")}</Link>
              <Link className={navCls(pathname, "/stats")} to="/stats">{t("nav.stats")}</Link>
              <Link className={navCls(pathname, "/profile-view")} to="/profile-view">{t("nav.profile")}</Link>
              <Link className={navCls(pathname, "/import-excel")} to="/import-excel">{t("nav.importFromExcel")}</Link>
            </>
          )}
        </nav>
        <div className="flex items-center gap-3">
          {user && (
            <span className="text-sm">Hi, {t("app.hiUser", { username: user.username })}</span>)}
          {user && <button className="btn" onClick={() => { logout(); navigate("/login"); }}>{t("nav.logout")}</button>}
        </div>
        {/* Language switcher */}
        <select
          className="border rounded px-2 py-1 text-sm"
          value={i18n.resolvedLanguage}
          onChange={(e) => i18n.changeLanguage(e.target.value)}
        >
          <option value="en_US">English - US</option>
          <option value="et_EE">Eesti</option>
        </select>
      </div>
    </header>
  );
}

function navCls(path: string, href: string) {
  const active = path.startsWith(href);
  return `px-3 py-1 rounded-lg ${active ? "bg-slate-900 text-white" : "hover:bg-slate-100"}`;
}
