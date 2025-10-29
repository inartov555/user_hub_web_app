import React, { useState } from "react";
import { NavLink, Link, useLocation, useNavigate } from "react-router-dom";
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
  // className="bg-gray-200 text-blue-800 border rounded px-2 py-1 text-sm flex items-center gap-2"
  // Unified tab styles
  const tabCls = (isActive: boolean) =>
    `px-3 py-1 rounded-lg transition-colors ${
      isActive
        ? "bg-slate-900 text-white"
        : "bg-gray-200 text-blue-800 hover:bg-slate-100"
    }`;
  // Helper: treat multiple routes as active for one tab
  const isProfileActive = pathname.startsWith("/profile-view") || pathname.startsWith("/profile-edit");

  return (
    <header className="sticky top-0 z-10 bg-white/70 backdrop-blur border-b border-slate-200">
      <div className="max-w-6xl mx-auto flex items-center justify-between p-3">
        <div className="rounded-full bg-gray-200">
          <Link to="/" className="font-semibold">{t("app.title")}</Link>
        </div>
        <nav className="flex gap-4">
          {user && (
            <>
              <NavLink
                to="/users"
                className={({ isActive }) => tabCls(isActive)}
              >
                {t("nav.users")}
              </NavLink>

              {/* Mark active for both /profile-view and /profile-edit */}
              <NavLink
                to="/profile-view"
                className={() => tabCls(isProfileActive)}
              >
                {t("nav.profile")}
              </NavLink>
            </>
          )}
          {user && user.is_staff && (
            <>
              <NavLink
                to="/stats"
                className={({ isActive }) => tabCls(isActive)}
              >
                {t("nav.stats")}
              </NavLink>

              <NavLink
                to="/settings"
                className={({ isActive }) => tabCls(isActive)}
              >
                {t("nav.settings")}
              </NavLink>

              <NavLink
                to="/import-excel"
                className={({ isActive }) => tabCls(isActive)}
              >
                {t("nav.importFromExcel")}
              </NavLink>
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
  // active if exact match or a sub-route
  const isActive = list.some((href) => {
    if (!href) return false;
    if (href === "/") return path === "/";
    return path === href || path.startsWith(href + "/");
  });

  const base =
    "border rounded px-2 py-1 text-sm flex items-center gap-2 transition-colors";
  const active =
    "bg-slate-900 text-white border-slate-900 shadow-sm";
  const inactive =
    "bg-gray-200 text-blue-800 hover:bg-slate-100";

  return `${base} ${isActive ? active : inactive}`;
}
