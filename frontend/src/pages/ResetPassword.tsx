import { useState } from "react";
import { api } from "../lib/axios";
import FormInput from "../components/FormInput";

export default function ResetPassword() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    await api.post("/auth/users/reset_password/", { email });
    setSent(true);
  }

  return (
    <div className="max-w-md mx-auto card">
      <h1 className="text-2xl font-semibold mb-4">Reset password</h1>
      {sent ? <p>Check console email backend for the reset link.</p> : (
        <form onSubmit={onSubmit} className="space-y-3">
          <FormInput placeholder="Email" type="email" value={email} onChange={e=>setEmail(e.target.value)} required />
          <button className="btn w-full" type="submit">Send reset email</button>
        </form>
      )}
    </div>
  );
}
