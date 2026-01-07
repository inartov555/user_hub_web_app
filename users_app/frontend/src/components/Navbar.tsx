import React, { useState, useEffect } from "react";
import { NavLink, Link, useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { MessageCircle } from "lucide-react";
import { api } from "../lib/axios";
import { extractApiError } from "../lib/httpErrors";
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
  const tabCls = (active: boolean) =>
  [
    "relative inline-flex items-center justify-center",
    "px-3 py-1.5 md:px-3.5 md:py-2",
    "rounded-2xl text-sm font-semibold tracking-tight",
    "transition-all duration-200",
    "focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2",
    active
      ? [
          "text-slate-900 dark:text-slate-50",
          "bg-white/80 dark:bg-slate-900/60",
          "shadow-soft ring-1 ring-slate-900/10 dark:ring-white/10",
          "backdrop-blur",
        ].join(" ")
      : [
          "text-slate-600 dark:text-slate-200/80",
          "hover:text-slate-900 dark:hover:text-slate-50",
          "hover:bg-white/60 dark:hover:bg-slate-900/40",
          "hover:shadow-sm",
        ].join(" "),
  ].join(" ");
  const indicatorCls = (active: boolean) =>
    active
      ? "absolute -bottom-1 left-1/2 h-[3px] w-10 -translate-x-1/2 rounded-full bg-gradient-to-r from-brand-500/70 via-fuchsia-500/60 to-sky-500/60"
      : "absolute -bottom-1 left-1/2 h-[3px] w-6 -translate-x-1/2 rounded-full bg-transparent";
  const isUsersActive = pathname.startsWith("/users");
  const isProfileActive = pathname.startsWith("/profile-view") || pathname.startsWith("/profile-edit");
  const isUserStatsActive = pathname.startsWith("/stats");
  const isSettingsActive = pathname.startsWith("/settings");
  const isExcelImportActive = pathname.startsWith("/import-excel");
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

  // When opening "Additional", show the 2nd row and select its first tab (/stats)
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
    <header className="
              sticky top-0 z-10 bg-white/70 backdrop-blur border-b border-slate-200 dark:bg-slate-800
              dark:text-slate-100 dark:border-slate-700
            "
    >
      {/* 3-column grid: Left (logo) | Middle (two tab rows) | Right (user/lang) */}
      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-[auto_1fr_auto] items-start gap-3 p-3"
           style={{ maxWidth: "1360px" }}
      >
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
                    <span aria-hidden="true" className={indicatorCls(isUsersActive && !isAdditionalActive)} />
                    {t("nav.users")}
                  </NavLink>

                  <NavLink
                    id="profile"
                    to="/profile-view"
                    className={() => tabCls(isProfileActive && !isAdditionalActive)}
                  >
                    <span aria-hidden="true" className={indicatorCls(isProfileActive && !isAdditionalActive)} />
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
                      <span aria-hidden="true" className={indicatorCls(isAdditionalActive)} />
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
                  <span aria-hidden="true" className={indicatorCls(isUserStatsActive)} />
                  {t("nav.stats")}
                </NavLink>
                <NavLink id="settings" to="/settings" className={({ isActive }) => tabCls(isActive)}>
                  <span aria-hidden="true" className={indicatorCls(isSettingsActive)} />
                  {t("nav.settings")}
                </NavLink>
                <NavLink id="excelImport" to="/import-excel" className={({ isActive }) => tabCls(isActive)}>
                  <span aria-hidden="true" className={indicatorCls(isExcelImportActive)} />
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
              {/* Greeting message */}
              <div
                className="
                  min-w-0 inline-flex items-center gap-2 rounded-full px-3 py-2 text-sm
                  border border-slate-200/70 bg-white/70 shadow-soft backdrop-blur
                  text-slate-800
                  dark:border-slate-700/70 dark:bg-slate-900/50 dark:text-slate-100
                "
              >
                <span
                  data-tag="greeting-icon"
                  className="
                    inline-flex h-8 w-8 items-center justify-center rounded-full
                    bg-gradient-to-br from-brand-600/80 to-indigo-600/60
                    text-white shadow-sm ring-1 ring-white/12
                    shrink-0
                  "
                >
                  <MessageCircle className="h-4 w-4" />
                </span>

                <span
                  id="greeting"
                  className="min-w-0 truncate"
                  title={t("app.hiUser", { username: user.username })}
                >
                  {t("app.hiUser", { username: user.username })}
                </span>
              </div>

              <Button
                id="logout"
                onClick={async () => {
                  logout();
                  try {
                    await api.post("/auth/jwt/logout/");
                  } catch (err: any) {
                    const parsed = extractApiError(err as unknown);
                    // setError(`${parsed.message}`);
                    console.log("Raw error: " + err)
                    console.log("Parsed error: " + parsed.message)
                  }
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
              className="
                border border-slate-300 dark:border-slate-700 rounded bg-white dark:bg-slate-900 px-2 py-1 text-sm
                text-slate-900 dark:text-slate-100 dark:[color-scheme:dark]
                dark:[&>option]:bg-slate-900 dark:[&>option]:text-slate-100
              "
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
