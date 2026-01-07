import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { BarChart3 } from "lucide-react";
import { api } from "../lib/axios";
import UnifiedTitle from "../components/UnifiedTitle";

export default function Stats() {
  const { t, i18n } = useTranslation();
  const { data } = useQuery({ queryKey: ["online-users"], queryFn: async () => (await api.get("/stats/online-users/")).data });
  return (
    <div className="
    	   relative overflow-hidden rounded-2xl border p-4
           bg-white/75 backdrop-blur shadow-soft ring-1 ring-slate-900/5
           dark:bg-slate-900/50 dark:border-slate-700/70 dark:text-slate-100 dark:ring-white/5
    	 "
    >
      <div aria-hidden
           className="
             pointer-events-none absolute inset-x-0 top-0 h-24
             bg-gradient-to-b from-brand-500/10 via-indigo-500/6 to-transparent
             dark:from-brand-400/12 dark:via-indigo-400/8
           "
      />
      <UnifiedTitle icon={<BarChart3 className="h-4 w-4" />} title={t("stats.curOnline5Mins")} />
      <ul className="list-disc pl-6">
        {(data ?? []).map((u: any) => (
          <li key={u.id}>{u.username} ({u.email})</li>
        ))}
      </ul>
    </div>
  );
}
