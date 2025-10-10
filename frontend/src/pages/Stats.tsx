import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/axios";

export default function Stats() {
  const { data } = useQuery({ queryKey: ["online-users"], queryFn: async () => (await api.get("/stats/online-users/")).data });
  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-3">Currently online users (last 5 minutes)</h2>
      <ul className="list-disc pl-6">
        {(data ?? []).map((u: any) => (
          <li key={u.id}>{u.username} ({u.email})</li>
        ))}
      </ul>
    </div>
  );
}
