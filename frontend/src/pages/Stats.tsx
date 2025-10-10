import * as React from 'react';
import api from '../lib/api';

type User = { id:number; username:string; last_seen: string };

export default function Stats() {
  const [users, setUsers] = React.useState<User[]>([]);
  React.useEffect(() => {
    (async () => {
      const { data } = await api.get('/stats/online-users/');
      setUsers(data);
    })();
  }, []);
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">Online users (last 5 minutes)</h1>
      <ul className="space-y-2">
        {users.map(u => (
          <li key={u.id} className="p-3 rounded-xl bg-white shadow">
            <div className="font-medium">{u.username}</div>
            <div className="text-xs text-gray-500">last seen: {new Date(u.last_seen).toLocaleString()}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}
