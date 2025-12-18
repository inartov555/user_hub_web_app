import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { api } from "../lib/axios";
import { Card, CardHeader, CardBody } from "../components/card";
import Button from "../components/button";
import { extractApiError } from "../lib/httpErrors";
import { useAuthStore } from "../auth/store";

type User = {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
};

type LocationState = { users?: User[] };

export default function UserDeleteConfirm() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const { state } = useLocation() as { state?: LocationState };
  const users = state?.users ?? [];
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!users.length) {
      // nothing to confirm
      navigate("/users", { replace: true });
    }
  }, [users.length, navigate]);

  const handleConfirm = async () => {
    const ids = users.map((u) => u.id);
    if (!ids.length) return;

    setLoading(true);
    setError(null);
    try {
      // Try bulk endpoint first
      const bulk = await api.post("/users/bulk-delete/", { ids }, { validateStatus: () => true });

      // Fallback retry user deletion, set validateStatus to true when you need it
      if (bulk.status < 200 || bulk.status >= 300) {
        const parsed = extractApiError(bulk);
        setError(prev => (prev ? `${prev}` : "") + `${t("userDeleteConfirm.failedToDeleteSelectedUsers")}\n\n`);
        setError(prev => (prev ? `${prev}` : "") + `${t("userDeleteConfirm.bulkDeleteFailed")} ${parsed.message}\n\n`);
        // Fallback to per-user delete
        const results = await Promise.allSettled(
          ids.map((id) => api.delete(`/users/${id}/delete-user/`, { validateStatus: () => true }))
        );
        const failed = results.filter(
	      (r) => r.status === "rejected" || (r.status === "fulfilled" && r.value.status > 204)
        );
        if (failed.length) {
          setError(prev => (prev ? `${prev}` : "") + `${t("userDeleteConfirm.singleDeleteFailed")}\n`);
          setError(prev => (prev ? `${prev}` : "") + `${t("userDeleteConfirm.failedToDelete")} ${failed.length} ${t("users.of")} ${ids.length} ${t("users.title")}.`);
          for (const err_item of failed) {
            const parsed = extractApiError(err_item);
            setError(prev => (prev ? `${prev}` : "") + `${parsed.message}`);
          }
        }
      }
      else {
        await qc.invalidateQueries({ queryKey: ["users"] });
        navigate("/users", { replace: true });
      }
    } catch (erro: any) {
      const parsed = extractApiError(erro);
      setError(prev => (prev ? `${prev}` : "") + `\n${t("userDeleteConfirm.failedToDeleteSelectedUsers")} ${parsed.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => navigate("/users");

  if (!users.length) return null;

  return (
    <Card className="w-full mx-auto max-w-3xl dark:bg-slate-800 dark:text-slate-100 dark:border-slate-700">
      <CardHeader title={t("userDeleteConfirm.confirmDelete")} />
      <CardBody className="space-y-4">
        <p className="text-sm text-slate-700 dark:text-slate-100">
          {t("userDeleteConfirm.youAboutToDelete")} <strong>{users.length}</strong> {t("userDeleteConfirm.cannotBeUndone")}
        </p>

        <div className="rounded-lg border overflow-hidden">
          <table className="w-full text-sm table-auto">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left px-3 py-2">{t("signup.username")}</th>
                <th className="text-left px-3 py-2">{t("signup.email")}</th>
                <th className="text-left px-3 py-2">{t("users.firstName")}</th>
                <th className="text-left px-3 py-2">{t("users.lastName")}</th>
              </tr>
            </thead>
            <tbody>
              {users.slice(0, 20).map((u) => (
                <tr key={u.id} className="border-t">
                  <td className="px-3 py-2">{u.username}</td>
                  <td className="px-3 py-2">{u.email}</td>
                  <td className="px-3 py-2">{u.first_name}</td>
                  <td className="px-3 py-2">{u.last_name}</td>
                </tr>
              ))}
              {users.length > 20 && (
                <tr className="border-t">
                  <td className="px-3 py-2 text-slate-500" colSpan={4}>
                    {t("userDeleteConfirm.and")} {users.length - 20} {t("userDeleteConfirm.more")}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {error && <div className="text-sm text-red-600 whitespace-pre-line">{error}</div>}

        <div className="flex items-center gap-2">
          <Button
            id="confirmDelete"
            className="border-red-600 text-red-700 hover:bg-red-50"
            variant="secondary"
            onClick={handleConfirm}
            disabled={loading}
            title={t("userDeleteConfirm.deleteUsers")}
          >
            {loading ? t("userDeleteConfirm.deleting") : `${t("users.deleteSelected")} ${users.length}`}
          </Button>
          <Button id="cancel" variant="secondary" className="border-red-600 text-red-700 hover:bg-red-50" onClick={handleCancel} disabled={loading}>
            {t("userDeleteConfirm.cancel")}
          </Button>
        </div>
      </CardBody>
    </Card>
  );
}
