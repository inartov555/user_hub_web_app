import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/axios";
import { Card, CardHeader, CardTitle, CardContent } from "../components/card";
import { Button } from "../components/button";
import { extractApiError } from "../lib/httpErrors";

type User = {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
};

type LocationState = { users?: User[] };

export default function UserDeleteConfirm() {
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

      if (!(bulk.status >= 200 && bulk.status < 300)) {
        // Fallback to per-user delete
        const results = await Promise.allSettled(
          ids.map((id) => api.delete(`/users/${id}/`, { validateStatus: () => true }))
        );
        const failed = results.filter(
          (r) => r.status === "rejected" || (r.status === "fulfilled" && r.value.status >= 400)
        );
        if (failed.length) {
          setError(`Failed to delete ${failed.length} of ${ids.length} users.`);
        }
      }

      let bulkOk = false;

      // Try bulk endpoint first.
      // First, let's make bulk-delete request WITHOUT validateStatus to catch 4xx/5xx and show the error message
      try {
        const bulk = await api.post("/users/bulk-delete/", { ids });
        bulkOk = bulk.status >= 200 && bulk.status < 300;
      } catch (err) {
  	const parsed = extractApiError(err as unknown);
  	setError(`Bulk delete failed: ${parsed.message}`);
  	bulkOk = false;
      }

      // If bulk failed, then delete users one by one
      if (!bulkOk) {
  	  const results = await Promise.allSettled(
   	  ids.map((id) => api.delete(`/users/${id}/`, { validateStatus: () => true }))
        );
        const failed = results.filter(
    	  (r) => r.status === "rejected" || (r.status === "fulfilled" && r.value.status >= 400)
        );
        if (failed.length) {
    	  setError(`User deletion failed: ${failed.length} of ${ids.length} users.`);
        }
      }

      await qc.invalidateQueries({ queryKey: ["users"] });
      navigate("/users", { replace: true });
    } catch (e: any) {
      setError(e?.message || "Failed to delete selected users.");
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => navigate("/users");

  if (!users.length) return null;

  return (
    <Card className="w-full mx-auto max-w-3xl">
      <CardHeader>
        <CardTitle>Confirm deletion</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-slate-700">
          You are about to permanently delete <strong>{users.length}</strong> user{users.length > 1 ? "s" : ""}.
          This action cannot be undone.
        </p>

        <div className="rounded-lg border overflow-hidden">
          <table className="w-full text-sm table-auto">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left px-3 py-2">Username</th>
                <th className="text-left px-3 py-2">Email</th>
                <th className="text-left px-3 py-2">First name</th>
                <th className="text-left px-3 py-2">Last name</th>
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
                    …and {users.length - 20} more
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {error && <div className="text-sm text-red-600">{error}</div>}

        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleCancel} disabled={loading}>
            Cancel
          </Button>
          <Button
            className="border-red-600 text-red-700 hover:bg-red-50"
            variant="outline"
            onClick={handleConfirm}
            disabled={loading}
            title="Delete users"
          >
            {loading ? "Deleting…" : `Delete ${users.length} selected`}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
