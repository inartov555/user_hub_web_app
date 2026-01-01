import React, { useState, useEffect } from "react";
import { NavLink, Link, useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../auth/store";
import i18n from "../lib/i18n";
import { LocaleFlag } from "../components/LocaleFlag";
import Brand from "../components/Brand";
import Button from "../components/button";
import DarkModeToggle from "../components/DarkModeToggle";

export default function Navbar() {
  const { t } = useTranslation();
  const [locale, setLocale] = useState(i18n.resolvedLanguage || "en-US");
  const { pathname } = useLocation();
  const { user, logout, accessToken } = useAuthStore();
  const navigate = useNavigate();
  // Unified tab styles
  const tabCls = (isActive: boolean) =>
  `px-3 py-1 rounded-lg transition-colors border ${
    isActive
      ? "bg-slate-900 text-white border-slate-900 shadow-soft"
      : "bg-white/60 text-slate-700 border-slate-200 hover:bg-white shadow-soft"
  }`;
  // Treat multiple routes as active for one tab
  const isProfileActive = pathname.startsWith("/profile-view") || pathname.startsWith("/profile-edit");
  // "Additional" tab logic
  const secondRowRoutes = ["/stats", "/settings", "/import-excel"];
  const routeIsSecondRow = secondRowRoutes.some((p) => pathname.startsWith(p));
  // Show row 2 if user clicked Additional or a second-row route is active
  const [additionalOpen, setAdditionalOpen] = useState(false);
  const isAdditionalActive = additionalOpen || routeIsSecondRow;

  // Close Additional whenever we navigate to a first-row route
  useEffect(() => {
    if (!routeIsSecondRow && additionalOpen) {
      setAdditionalOpen(false);
    }
  }, [pathname, routeIsSecondRow, additionalOpen]);

  // When opening "Additional", show row 2 and select its first tab (/stats)
  const onToggleAdditional = () => {
    setAdditionalOpen((prev) => {
      const next = !prev;
      if (next && !routeIsSecondRow) {
        navigate("/stats");
      }
      return next;
    });
  };

  return (
    <header className="sticky top-0 z-10 bg-white/70 backdrop-blur border-b border-slate-200 dark:bg-slate-800 dark:text-slate-100 dark:border-slate-700">
      {/* 3-column grid: Left (logo) | Middle (two tab rows) | Right (user/lang) */}
      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-[auto_1fr_auto] items-start gap-3 p-3">
        {/* Left: app title */}
        <div className="justify-self-start">
          <Brand title={t("app.title")} />
        </div>

        {/* Middle: TWO ROWS, left-aligned; row 2 starts exactly under row 1 */}
        <div className="justify-self-start w-full">
          <div className="flex flex-col gap-2 items-start">
            {/* Row 1 */}
            <nav className="flex flex-wrap gap-2 md:gap-4">
              {user && (
                <>
                  {/* While Additional is active, force row-1 tabs to look inactive */}
                  <NavLink
                    id="users"
                    to="/users"
                    className={({ isActive }) => tabCls(isActive && !isAdditionalActive)}
                  >
                    {t("nav.users")}
                  </NavLink>

                  <NavLink
                    id="profile"
                    to="/profile-view"
                    className={() => tabCls(isProfileActive && !isAdditionalActive)}
                  >
                    {t("nav.profile")}
                  </NavLink>

                  {/* Additional tab (first row) — reveals row 2 */}
                  {user?.is_staff && (
                    <button
                      id="additional"
                      type="button"
                      className={tabCls(isAdditionalActive)}
                      onClick={onToggleAdditional}
                      aria-expanded={isAdditionalActive}
                      aria-controls="secondary-nav"
                    >
                      {t("nav.additional")}
                    </button>
                  )}
                </>
              )}
            </nav>

            {/* Row 2 - hidden until Additional is active or a second-row route is active */}
            {user?.is_staff && isAdditionalActive && (
              <nav id="secondary-nav" className="flex flex-wrap gap-2 md:gap-4">
                <NavLink id="userStats" to="/stats" className={({ isActive }) => tabCls(isActive)}>
                  {t("nav.stats")}
                </NavLink>
                <NavLink id="settings" to="/settings" className={({ isActive }) => tabCls(isActive)}>
                  {t("nav.settings")}
                </NavLink>
                <NavLink id="excelImport" to="/import-excel" className={({ isActive }) => tabCls(isActive)}>
                  {t("nav.importFromExcel")}
                </NavLink>
              </nav>
            )}
          </div>
        </div>

        {/* Right: user + language */}
        <div className="flex items-center gap-3 justify-self-end">
          {user && (
            <>
              <div className="bg-gray-200 border rounded-full px-2 py-1 text-sm flex items-center gap-2 dark:bg-slate-900 dark:text-slate-100 dark:placeholder-slate-500
            dark:border-slate-700">
                <span id="greeting" className="text-sm">
                  {t("app.hiUser", { username: user.username })}
                </span>
              </div>
              <Button
                id="logout"
                onClick={() => {
                  logout();
                  navigate("/login");
                }}
              >
                {t("nav.logout")}
              </Button>
            </>
          )}

          {/* Language switcher */}
          <div className="bg-gray-200 border rounded-full px-2 py-1 text-sm flex items-center gap-2">
            <span className="bg-gray-200 border border-transparent rounded px-2 py-1 text-sm flex items-center gap-2">
              <LocaleFlag locale={locale} size={24} />
            </span>
            <select
              id="locale"
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
            <DarkModeToggle />
          </div>
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
