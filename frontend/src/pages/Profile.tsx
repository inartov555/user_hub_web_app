import * as React from 'react';
import api from '../lib/api';

type Me = { username:string; email:string; first_name:string; last_name:string; title:string; avatar?: string };

export default function Profile() {
  const [me, setMe] = React.useState<Me | null>(null);
  const [first_name, setFirst] = React.useState('');
  const [last_name, setLast] = React.useState('');
  const [title, setTitle] = React.useState('');

  React.useEffect(() => {
    (async () => {
      const { data } = await api.get('/users/me/');
      setMe(data);
      setFirst(data.first_name || '');
      setLast(data.last_name || '');
      setTitle(data.title || '');
    })();
  }, []);

  async function saveProfile(e: React.FormEvent) {
    e.preventDefault();
    const { data } = await api.patch('/users/me/', { first_name, last_name, title });
    setMe(data);
  }

  async function onAvatarChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0]; if (!f) return;
    const form = new FormData(); form.append('avatar', f);
    await api.patch('/users/me/avatar/', form, { headers: { 'Content-Type': 'multipart/form-data' }});
    const { data } = await api.get('/users/me/'); setMe(data);
  }

  async function onExcelChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0]; if (!f) return;
    const form = new FormData(); form.append('file', f);
    const { data } = await api.post('/users/import-excel/', form);
    alert(`Created: ${data.created}, Updated: ${data.updated}`);
  }

  if (!me) return <div className="p-6">Loading...</div>;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-semibold">My Profile</h1>

      <form onSubmit={saveProfile} className="space-y-4 max-w-xl">
        <div className="grid grid-cols-2 gap-4">
          <label className="block">
            <span className="text-sm">First name</span>
            <input className="w-full border rounded px-3 py-2" value={first_name} onChange={(e)=>setFirst(e.target.value)} />
          </label>
          <label className="block">
            <span className="text-sm">Last name</span>
            <input className="w-full border rounded px-3 py-2" value={last_name} onChange={(e)=>setLast(e.target.value)} />
          </label>
        </div>
        <label className="block">
          <span className="text-sm">Title</span>
          <input className="w-full border rounded px-3 py-2" value={title} onChange={(e)=>setTitle(e.target.value)} />
        </label>
        <button className="px-4 py-2 rounded bg-black text-white">Save</button>
      </form>

      <div className="max-w-xl space-y-4">
        <div>
          <div className="text-sm font-medium mb-1">Avatar</div>
          <input type="file" accept="image/*" onChange={onAvatarChange} />
          {me.avatar && <img src={me.avatar} alt="avatar" className="mt-2 w-24 h-24 rounded-full object-cover" />}
        </div>
        <div>
          <div className="text-sm font-medium mb-1">Import users via Excel (.xlsx)</div>
          <input type="file" accept=".xlsx" onChange={onExcelChange} />
        </div>
      </div>
    </div>
  );
}
