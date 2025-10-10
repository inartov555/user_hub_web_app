import * as React from 'react';
import { login } from '../lib/auth';
import { useNavigate, Link } from 'react-router-dom';

export default function Login() {
  const nav = useNavigate();
  const [username, setU] = React.useState('');
  const [password, setP] = React.useState('');

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    await login(username, password);
    nav('/users');
  }

  return (
    <div className="max-w-sm mx-auto p-6 bg-white rounded-2xl shadow">
      <h1 className="text-xl font-semibold mb-4">Log in</h1>
      <form onSubmit={submit} className="space-y-3">
        <input className="w-full border rounded px-3 py-2" placeholder="Username" value={username} onChange={e=>setU(e.target.value)} />
        <input type="password" className="w-full border rounded px-3 py-2" placeholder="Password" value={password} onChange={e=>setP(e.target.value)} />
        <button className="w-full px-4 py-2 rounded bg-black text-white">Log in</button>
      </form>
      <div className="text-sm mt-3 flex justify-between">
        <Link to="/signup" className="underline">Create account</Link>
        <Link to="/reset" className="underline">Forgot password?</Link>
      </div>
    </div>
  );
}
