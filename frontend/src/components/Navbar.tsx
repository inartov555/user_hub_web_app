import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../auth/store";
import { LocaleFlag } from "./LocaleFlag";

export default function Navbar() {
  const { t, i18n } = useTranslation();
  const [locale, setLocale] = useState(i18n.resolvedLanguage || "en-US");
  const { pathname } = useLocation();
  const { user, logout, accessToken } = useAuthStore();
  const navigate = useNavigate();
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
            <span className="text-sm">{t("app.hiUser", { username: user.username })}</span>)}
          {user && <button className="btn" onClick={() => { logout(); navigate("/login"); }}>{t("nav.logout")}</button>}
        </div>
        {/* Language switcher */}
        {/* Show current flag next to the select */}
        <div>
    	  <LocaleFlag locale={locale} size={18} />
          <select
            className="border rounded px-2 py-1 text-sm"
            value={locale}
            onChange={(e) => {
              const next = e.target.value;
              setLocale(next);
              i18n.changeLanguage(next);
            }}
          >
            <option value="en-US">English - US</option>
            <option value="et-EE">Eesti</option>
          </select>
        </div>
      </div>
    </header>
  );
}

function navCls(path: string, href: string) {
  const active = path.startsWith(href);
  return `px-3 py-1 rounded-lg ${active ? "bg-slate-900 text-white" : "hover:bg-slate-100"}`;
}
