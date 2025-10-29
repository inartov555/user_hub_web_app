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
          
          
          
          {/* Additional tab with dropdown for Stats / Settings / Import */}
          {user && user.is_staff && (
            <>
          <div className="relative group">
            <button
              type="button"
              className={navCls(pathname, ["/stats", "/settings", "/import-excel"])}
              aria-haspopup="menu"
            >
              {t("nav.additional", "Additional")}
              <span className="ml-1 inline-block align-middle">▾</span>
            </button>

            {/* stays open when hovering trigger or panel, and when keyboard focusing links */}
            <div
              className="absolute right-0 mt-2 w-56 rounded-lg border border-slate-200 bg-white shadow-lg p-2
                         hidden group-hover:block group-focus-within:block"
              role="menu"
              aria-label="Additional"
            >
              {/* Stats – visible to any logged-in user */}
              <Link
                to="/stats"
                className={dropdownItemCls(pathname.startsWith("/stats"))}
                role="menuitem"
              >
                {t("nav.stats")}
              </Link>

              {/* Staff-only */}
              {user?.is_staff && (
                <>
                  <Link
                    to="/settings"
                    className={dropdownItemCls(pathname.startsWith("/settings"))}
                    role="menuitem"
                  >
                    {t("nav.settings")}
                  </Link>
                  <Link
                    to="/import-excel"
                    className={dropdownItemCls(pathname.startsWith("/import-excel"))}
                    role="menuitem"
                  >
                    {t("nav.importFromExcel")}
                  </Link>
                </>
              )}
            </div>
          </div>
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
        
        
        <nav className="flex gap-4">
        
        
                  {/* Additional tab with dropdown for Stats / Settings / Import */}
          {user && user.is_staff && (
            <>
          <div className="relative group">
            <button
              type="button"
              className={navCls(pathname, ["/stats", "/settings", "/import-excel"])}
              aria-haspopup="menu"
            >
              {t("nav.additional", "Additional")}
              <span className="ml-1 inline-block align-middle">▾</span>
            </button>

            {/* stays open when hovering trigger or panel, and when keyboard focusing links */}
            <div
              className="absolute right-0 mt-2 w-56 rounded-lg border border-slate-200 bg-white shadow-lg p-2
                         hidden group-hover:block group-focus-within:block"
              role="menu"
              aria-label="Additional"
            >
              {/* Stats – visible to any logged-in user */}
              <Link
                to="/stats"
                className={dropdownItemCls(pathname.startsWith("/stats"))}
                role="menuitem"
              >
                {t("nav.stats")}
              </Link>

              {/* Staff-only */}
              {user?.is_staff && (
                <>
                  <Link
                    to="/settings"
                    className={dropdownItemCls(pathname.startsWith("/settings"))}
                    role="menuitem"
                  >
                    {t("nav.settings")}
                  </Link>
                  <Link
                    to="/import-excel"
                    className={dropdownItemCls(pathname.startsWith("/import-excel"))}
                    role="menuitem"
                  >
                    {t("nav.importFromExcel")}
                  </Link>
                </>
              )}
            </div>
          </div>
              </>
          )}
          
          
          
          
        </nav>
        
        
        
        <nav className="flex gap-4">

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
  // Tab active/inactive styles
  const list = Array.isArray(hrefs) ? hrefs : [hrefs];
  const active = list.some((h) => path.startsWith(h));
  return `px-3 py-1 rounded-lg ${
    active ? "bg-slate-900 text-white" : "hover:bg-slate-100"
  }`;
}

function dropdownItemCls(active: boolean) {
  return `block w-full text-left px-3 py-2 rounded-md text-sm ${
    active ? "bg-slate-100 font-medium" : "hover:bg-slate-50"
  }`;
}
