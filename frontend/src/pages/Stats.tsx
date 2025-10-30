import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { api } from "../lib/axios";

export default function Stats() {
  const { t, i18n } = useTranslation();
  const { data } = useQuery({ queryKey: ["online-users"], queryFn: async () => (await api.get("/stats/online-users/")).data });
  return (
    <div className="max-w-xl mx-auto p-4 rounded-2xl shadow bg-white border">
      <h2 className="text-xl font-semibold mb-3">{t("stats.curOnline5Mins")}</h2>
      <ul className="list-disc pl-6">
        {(data ?? []).map((u: any) => (
          <li key={u.id}>{u.username} ({u.email})</li>
        ))}
      </ul>
    </div>
  );
}
