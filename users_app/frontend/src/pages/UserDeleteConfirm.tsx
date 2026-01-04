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
import { SimpleErrorMessage } from "../components/ErrorAlert";

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
  const [remainingUsers, setRemainingUsers] = useState<User[]>(() => users);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!remainingUsers.length) {
      // nothing to confirm
      navigate("/users", { replace: true });
    }
  }, [remainingUsers.length, navigate]);

  const handleConfirm = async () => {
    const ids = remainingUsers.map((u) => u.id);
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
        // Fallback (on-by-one user deletion)
        const results = await Promise.allSettled(
          ids.map((id) => api.delete(`/users/${id}/delete-user/`, { validateStatus: () => true }))
        );

        const failed = results.filter(
	      (res1) => res1.status === "rejected" || (res1.status === "fulfilled" && res1.value.status > 204)
        );

        if (failed.length) {
          const failedReqUsers: User[] = [];

          setError(prev => (prev ? `${prev}` : "") + `${t("userDeleteConfirm.singleDeleteFailed")}\n`);
          setError(prev => (prev ? `${prev}` : "") + `${t("userDeleteConfirm.failedToDelete")} ${failed.length} ${t("users.of")} ${ids.length} ${t("users.title")}.\n`);

          for (let idx = 0; idx < results.length; idx++) {
            const id = ids[idx];
            const res = results[idx];

            if (res.status === "rejected") {
              const parsed = extractApiError(res.reason);
              const msg = (parsed?.message ?? "").trim();
              if (msg) setError(prev => (prev ? `${prev}` : "") + `${id}: ${msg}\n`);
              for (const _user of users) {
                if (_user.id === id) {
                  failedReqUsers.push(_user);
                }
              }
            } else {
              // res.value.status > 204
              const resp = res.value;
              if (resp.status > 204) {
                const parsed = extractApiError(resp);
                const msg = (parsed?.message ?? "").trim();
                if (msg) setError(prev => (prev ? `${prev}` : "") + `${id}: ${msg}\n`);
                for (const _user of users) {
                  if (_user.id === id) {
                    failedReqUsers.push(_user);
                  }
                }
              }
            }
          }
          setRemainingUsers(failedReqUsers);
        }
      }
      else {
        await qc.invalidateQueries({ queryKey: ["users"] });
        navigate("/users", { replace: true });
      }
    } catch (erro: any) {
      const parsed = extractApiError(erro);
      setError(prev => "This is a debug message to check");
      setError(prev => (prev ? `${prev}` : "") + `\n${t("userDeleteConfirm.failedToDeleteSelectedUsers")} ${parsed.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => navigate("/users");

  if (!remainingUsers.length) return null;

  return (
    <Card className="w-full mx-auto max-w-3xl dark:bg-slate-800 dark:text-slate-100 dark:border-slate-700">
      <CardHeader icon=<UserX className="h-4 w-4" /> title={t("userDeleteConfirm.confirmDelete")} />
      <CardBody className="space-y-4">
        <p className="text-sm text-slate-700 dark:text-slate-100">
          {t("userDeleteConfirm.youAboutToDelete")} <strong>{remainingUsers.length}</strong> {t("userDeleteConfirm.cannotBeUndone")}
        </p>

        {/* Top button pair */}
        <div className="flex gap-2">
          <Button
            id="confirmDeleteTop"
            onClick={handleConfirm}
            disabled={loading}
            title={t("userDeleteConfirm.deleteUsers")}
          >
            <Trash2 className="h-4 w-4" />
            {loading ? t("userDeleteConfirm.deleting") : `${t("users.deleteSelected")} (${remainingUsers.length})`}
          </Button>
          <Button id="cancelTop" onClick={handleCancel} disabled={loading}>
            {t("userDeleteConfirm.cancel")}
          </Button>
        </div>

        {/* The user list to delete */}
        <div className="rounded-lg border overflow-hidden">
          <table className="w-full text-sm table-auto">
            <thead className="bg-muted/50">
              <tr className="divide-x divide-slate-300 dark:divide-slate-600 border-b border-slate-300 dark:border-slate-600">
                <th data-tag="header-userId"
                    className="
                      bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-slate-100
                      relative select-none px-3 py-2 text-left font-semibold align-middle
                      whitespace-normal break-words text-center
                      hover:bg-slate-400/80 dark:hover:bg-slate-400/80 dark:hover:text-slate-100
                    "
                >
                  {t("userDeleteConfirm.userId")}
                </th>
                <th data-tag="header-username"
                    className="
                      bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-slate-100
                      relative select-none px-3 py-2 text-left font-semibold align-middle
                      whitespace-normal break-words text-center
                      hover:bg-slate-400/80 dark:hover:bg-slate-400/80 dark:hover:text-slate-100
                    "
                >
                  {t("signup.username")}
                </th>
                <th data-tag="header-email"
                    className="
                      bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-slate-100
                      relative select-none px-3 py-2 text-left font-semibold align-middle
                      whitespace-normal break-words text-center
                      hover:bg-slate-400/80 dark:hover:bg-slate-400/80 dark:hover:text-slate-100
                    "
                >
                  {t("signup.email")}
                </th>
                <th data-tag="header-firstName"
                    className="
                      bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-slate-100
                      relative select-none px-3 py-2 text-left font-semibold align-middle
                      whitespace-normal break-words text-center
                      hover:bg-slate-400/80 dark:hover:bg-slate-400/80 dark:hover:text-slate-100
                    "
                >
                  {t("users.firstName")}
                </th>
                <th data-tag="header-lastName"
                    className="
                      bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-slate-100
                      relative select-none px-3 py-2 text-left font-semibold align-middle
                      whitespace-normal break-words text-center
                      hover:bg-slate-400/80 dark:hover:bg-slate-400/80 dark:hover:text-slate-100
                    "
                >
                  {t("users.lastName")}
                </th>
              </tr>
            </thead>
            <tbody>
              {remainingUsers.slice(0, 20).map((row) => (
                <tr data-tag={"row-userId-" + row.id}
                    className="
                      border-b divide-x divide-slate-300 dark:divide-slate-600
                      hover:bg-slate-400/80 dark:hover:bg-slate-400/80 dark:hover:text-slate-100
                    "
                >
                  <td data-tag={"cell-userId"}
                      className="px-3 py-2 align-middle whitespace-normal break-words"
                      style={{ overflowWrap: "anywhere", wordBreak: "break-word", whiteSpace: "pre-wrap" }}
                  >
                    {row.id}
                  </td>
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
              {remainingUsers.length > 20 && (
                <tr className="border-t">
                  <td className="px-3 py-2 text-slate-500"
                      colSpan={4}
                  >
                    {t("userDeleteConfirm.and")} {remainingUsers.length - 20} {t("userDeleteConfirm.more")}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {error && <SimpleErrorMessage errorBackend={error} />}

        {/* Bottom button pair */}
        <div className="flex gap-2">
          <Button
            id="confirmDeleteBottom"
            onClick={handleConfirm}
            disabled={loading}
            title={t("userDeleteConfirm.deleteUsers")}
          >
            <Trash2 className="h-4 w-4" />
            {loading ? t("userDeleteConfirm.deleting") : `${t("users.deleteSelected")} (${remainingUsers.length})`}
          </Button>
          <Button id="cancelBottom" onClick={handleCancel} disabled={loading}>
            {t("userDeleteConfirm.cancel")}
          </Button>
        </div>
      </CardBody>
    </Card>
  );
}
