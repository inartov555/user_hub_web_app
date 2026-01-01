import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { BarChart3 } from "lucide-react";
import { api } from "../lib/axios";
import UnifiedTitle from "../components/UnifiedTitle";

export default function Stats() {
  const { t, i18n } = useTranslation();
  const { data } = useQuery({ queryKey: ["online-users"], queryFn: async () => (await api.get("/stats/online-users/")).data });
  return (
    <div className="max-w-xl mx-auto p-4 rounded-2xl shadow bg-white border dark:bg-slate-800 dark:text-slate-100 dark:border-slate-700">
      <UnifiedTitle icon=<BarChart3 className="h-4 w-4" /> title={t("stats.curOnline5Mins")} />
      <ul className="list-disc pl-6">
        {(data ?? []).map((u: any) => (
          <li key={u.id}>{u.username} ({u.email})</li>
        ))}
      </ul>
    </div>
  );
}
