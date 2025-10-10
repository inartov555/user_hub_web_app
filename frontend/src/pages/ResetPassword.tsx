import * as React from 'react';
import { Link } from 'react-router-dom';

export default function ResetPassword() {
  const [identifier, setId] = React.useState('');

  function submit(e: React.FormEvent) {
    e.preventDefault();
    alert('In a production app, this would trigger an email-based reset flow. For now, contact an admin.');
  }

  return (
    <div className="max-w-sm mx-auto p-6 bg-white rounded-2xl shadow">
      <h1 className="text-xl font-semibold mb-4">Reset password</h1>
      <form onSubmit={submit} className="space-y-3">
        <input className="w-full border rounded px-3 py-2" placeholder="Username or email" value={identifier} onChange={e=>setId(e.target.value)} />
        <button className="w-full px-4 py-2 rounded bg-black text-white">Send reset instructions</button>
      </form>
      <div className="text-sm mt-3">
        <Link className="underline" to="/login">Back to login</Link>
      </div>
    </div>
  );
}
