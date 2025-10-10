import * as React from 'react';
import { register } from '../lib/auth';
import { Link, useNavigate } from 'react-router-dom';

export default function Signup() {
  const nav = useNavigate();
  const [username, setU] = React.useState('');
  const [email, setE] = React.useState('');
  const [password, setP] = React.useState('');

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    await register(username, email, password);
    nav('/login');
  }

  return (
    <div className="max-w-sm mx-auto p-6 bg-white rounded-2xl shadow">
      <h1 className="text-xl font-semibold mb-4">Sign up</h1>
      <form onSubmit={submit} className="space-y-3">
        <input className="w-full border rounded px-3 py-2" placeholder="Username" value={username} onChange={e=>setU(e.target.value)} />
        <input className="w-full border rounded px-3 py-2" placeholder="Email" value={email} onChange={e=>setE(e.target.value)} />
        <input type="password" className="w-full border rounded px-3 py-2" placeholder="Password" value={password} onChange={e=>setP(e.target.value)} />
        <button className="w-full px-4 py-2 rounded bg-black text-white">Create account</button>
      </form>
      <div className="text-sm mt-3">
        Have an account? <Link to="/login" className="underline">Log in</Link>
      </div>
    </div>
  );
}
