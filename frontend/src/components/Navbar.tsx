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
  // Controls the "Additional" dropdown
  const [moreOpen, setMoreOpen] = useState(false);

  return (
    <header className="sticky top-0 z-10 bg-white/70 backdrop-blur border-b border-slate-200">
      <div className="max-w-6xl mx-auto flex items-center justify-between p-3">
        <div className="rounded-full bg-gray-200">
          <Link to="/" className="font-semibold">{t("app.title")}</Link>
        </div>
        <nav className="flex gap-4">
          {user && (
            <>
              <div className="bg-gray-200 text-blue-800 border rounded px-2 py-1 text-sm flex items-center gap-2">
                <Link className={`navCls(pathname, "/users")`} to="/users">{t("nav.users")}</Link>
              </div>
              <div className="bg-gray-200 text-blue-800 border rounded px-2 py-1 text-sm flex items-center gap-2">
                <Link className={`navCls(pathname, ["/profile-view", "/profile-edit"])`} to="/profile-view">{t("nav.profile")}</Link>
              </div>
            </>
          )}
          {user && user.is_staff && (
            <>
              <div className="bg-gray-200 text-blue-800 border rounded px-2 py-1 text-sm flex items-center gap-2">
                <Link className={`navCls(pathname, "/stats"), bg-gray-200`} to="/stats">{t("nav.stats")}</Link>
              </div>
              <div className="bg-gray-200 text-blue-800 border rounded px-2 py-1 text-sm flex items-center gap-2">
	        <Link className={`navCls(pathname, "/settings"), bg-gray-200`} to="/settings">{t("nav.settings")}</Link>
	      </div>
	      <div className="bg-gray-200 text-blue-800 border rounded px-2 py-1 text-sm flex items-center gap-2">
	        <Link className={`navCls(pathname, "/import-excel"), bg-gray-200`} to="/import-excel">{t("nav.importFromExcel")}</Link>
	      </div>
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
        <div className="bg-gray-200 border rounded-full px-2 py-1 text-sm flex items-center gap-2">
          <span
            className="bg-gray-200 border border-transparent rounded px-2 py-1 text-sm flex items-center gap-2"
          >
    	    <LocaleFlag locale={locale} size={22} />
    	  </span>
          <select
            className="border border-slate-300 dark:border-slate-700 rounded bg-white dark:bg-slate-900 px-2 py-1 text-sm"
            value={locale}
            onChange={(e) => {
              const next = e.target.value;
              setLocale(next);
              i18n.changeLanguage(next);
            }}
          >
            <option value="en-US">English - US</option>
            <option value="uk-UA">Українська</option>
            <option value="et-EE">Eesti</option>
            <option value="fi-FI">Suomi</option>
            <option value="cs-CZ">Čeština</option>
            <option value="pl-PL">Polszczyzna</option>
            <option value="es-ES">Español</option>
          </select>
        </div>
      </div>
    </header>
  );
}

function navCls(path: string, hrefs: string | string[]) {
  // This function is responsible for tab activity/inactivity styles
  const list = Array.isArray(hrefs) ? hrefs : [hrefs];

  // Active if the path equals the href OR starts with "href/"
  const isActive = list.some((href) => {
    if (!href) return false;
    if (href === "/") return path === "/";
    return path === href || path.startsWith(href + "/");
  });

  const base =
    "px-3 py-1 rounded-lg transition-colors outline-none focus-visible:ring-2 focus-visible:ring-blue-500";
  const active =
    "bg-blue-700 text-white shadow-sm";
  const inactive =
    "text-blue-800 hover:bg-slate-100";

  return `${base} ${isActive ? active : inactive}`;
}
