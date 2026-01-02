import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { Trash2, UserX } from "lucide-react";
import { api } from "../lib/axios";
import { extractApiError } from "../lib/httpErrors";
import { useAuthStore } from "../auth/store";
import { Card, CardHeader, CardBody } from "../components/card";
import Button from "../components/button";
import PasswordInput from "../components/PasswordInput";

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
      // Bulk user deletion
      const bulk = await api.post("/users/bulk-delete/", { ids }, { validateStatus: () => true });

      // Uncomment this block to have additional user deletion one by one
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
      <CardHeader icon=<UserX className="h-4 w-4" /> title={t("userDeleteConfirm.confirmDelete")} />
      <CardBody className="space-y-4">
        <p className="text-sm text-slate-700 dark:text-slate-100">
          {t("userDeleteConfirm.youAboutToDelete")} <strong>{users.length}</strong> {t("userDeleteConfirm.cannotBeUndone")}
        </p>

        <div className="rounded-lg border overflow-hidden">
          <table className="w-full text-sm table-auto">
            <thead className="bg-muted/50">
              <tr className="divide-x divide-slate-300 dark:divide-slate-600 border-b border-slate-300 dark:border-slate-600">
                <th data-tag="header-username"
                    className="
                      bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-slate-100
                      relative select-none px-3 py-2 text-left font-semibold align-middle
                      whitespace-normal break-words text-center
                      hover:bg-slate-200/80 dark:hover:bg-slate-800/70
                    "
                >
                  {t("signup.username")}
                </th>
                <th data-tag="header-email"
                    className="
                      bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-slate-100
                      relative select-none px-3 py-2 text-left font-semibold align-middle
                      whitespace-normal break-words text-center
                      hover:bg-slate-200/80 dark:hover:bg-slate-800/70
                    "
                >
                  {t("signup.email")}
                </th>
                <th data-tag="header-firstName"
                    className="
                      bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-slate-100
                      relative select-none px-3 py-2 text-left font-semibold align-middle
                      whitespace-normal break-words text-center
                      hover:bg-slate-200/80 dark:hover:bg-slate-800/70
                    "
                >
                  {t("users.firstName")}
                </th>
                <th data-tag="header-lastName"
                    className="
                      bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-slate-100
                      relative select-none px-3 py-2 text-left font-semibold align-middle
                      whitespace-normal break-words text-center
                      hover:bg-slate-200/80 dark:hover:bg-slate-800/70
                    "
                >
                  {t("users.lastName")}
                </th>
              </tr>
            </thead>
            <tbody>
              {users.slice(0, 20).map((row) => (
                <tr data-tag={"row-userId-" + row.id}
                    className="
                      border-b divide-x divide-slate-300 dark:divide-slate-600
                      hover:bg-slate-200/70 dark:hover:bg-slate-200/80 dark:hover:text-slate-900
                    "
                >
                  <td data-tag={"cell-username"}
                      className="px-3 py-2 align-middle whitespace-normal break-words"
                      style={{ overflowWrap: "anywhere", wordBreak: "break-word", whiteSpace: "pre-wrap" }}
                  >
                    {row.username}
                  </td>
                  <td data-tag={"cell-email"}
                      className="px-3 py-2 align-middle whitespace-normal break-words"
                      style={{ overflowWrap: "anywhere", wordBreak: "break-word", whiteSpace: "pre-wrap" }}
                  >
                    {row.email}
                  </td>
                  <td data-tag={"cell-first_name"}
                      className="px-3 py-2 align-middle whitespace-normal break-words"
                      style={{ overflowWrap: "anywhere", wordBreak: "break-word", whiteSpace: "pre-wrap" }}
                  >
                    {row.first_name}
                  </td>
                  <td data-tag={"cell-last_name"}
                      className="px-3 py-2 align-middle whitespace-normal break-words"
                      style={{ overflowWrap: "anywhere", wordBreak: "break-word", whiteSpace: "pre-wrap" }}
                  >
                    {row.last_name}
                  </td>
                </tr>
              ))}
              {users.length > 20 && (
                <tr className="border-t">
                  <td className="px-3 py-2 text-slate-500"
                      colSpan={4}
                  >
                    {t("userDeleteConfirm.and")} {users.length - 20} {t("userDeleteConfirm.more")}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {error && <div className="text-sm text-red-600 whitespace-pre-line">{error}</div>}

        <div className="flex gap-2">
          <Button
            id="confirmDelete"
            onClick={handleConfirm}
            disabled={loading}
            title={t("userDeleteConfirm.deleteUsers")}
          >
            <Trash2 className="h-4 w-4" />
            {loading ? t("userDeleteConfirm.deleting") : `${t("users.deleteSelected")} (${users.length})`}
          </Button>
          <Button id="cancel" onClick={handleCancel} disabled={loading}>
            {t("userDeleteConfirm.cancel")}
          </Button>
        </div>
      </CardBody>
    </Card>
  );
}
