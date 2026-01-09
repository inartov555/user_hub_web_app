import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { BarChart3, Mail } from "lucide-react";
import { api } from "../lib/axios";
import UnifiedTitle from "../components/UnifiedTitle";
import { Card } from "../components/card";

export default function Stats() {
  const { t, i18n } = useTranslation();
  const { data } = useQuery({ queryKey: ["online-users"], queryFn: async () => (await api.get("/stats/online-users/")).data });
  return (
    <Card className="w-full mx-auto max-w-3xl">
      <UnifiedTitle icon={<BarChart3 className="h-4 w-4" />} title={t("stats.curOnline5Mins")} />
      {/*
      <ul className="list-disc pl-6">
        {(data ?? []).map((u: any) => (
          <li key={u.id}>{u.username} ({u.email})</li>
        ))}
      </ul>
      */}
      <ul className="
            divide-y divide-slate-200/70 rounded-2xl border
            bg-white/70 shadow-sm ring-1 ring-slate-900/5
            dark:divide-slate-700/70 dark:border-slate-700/70
            dark:bg-slate-900/40 dark:ring-white/5
          "
      >
        {(data ?? []).map((usr: any) => {
          const initials = (usr.username?.[0] ?? "U").toUpperCase();
          const fullName = [usr.first_name, usr.last_name].filter(Boolean).join(" ").trim();
          const tooltip = fullName || usr.email || initials;
          return (
            <li data-tag={`userId-${usr.id}-username-${usr.username}`}
                key={usr.id}
                className="flex items-center justify-between gap-3 p-3"
                title={tooltip}
            >
              <div className="min-w-0 flex items-center gap-3">
                <div className="
                       shrink-0 inline-flex h-9 w-9 items-center justify-center rounded-xl
                       text-white text-xs font-bold shadow-soft ring-1 ring-white/10
                       bg-gradient-to-br from-brand-600/80 to-indigo-600/60
                     "
                >
                  {initials}
                </div>

                <div className="min-w-0">
                  <div data-tag={`username-${usr.username}`} className="truncate font-semibold text-slate-900 dark:text-slate-50">
                    {usr.username}
                  </div>
                  <div data-tag={`email-${usr.email}`} className="truncate text-xs text-slate-600 dark:text-slate-300">
                    {usr.email}
                  </div>
                </div>
              </div>

              <div className="shrink-0 inline-flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                <Mail className="h-4 w-4" />
              </div>
            </li>
          );
        })}
      </ul>
    </Card>
  );
}
