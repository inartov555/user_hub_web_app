import { useState } from "react";
import { api } from "../lib/axios";
import { useAuthStore } from "../auth/store";
import FormInput from "../components/FormInput";
import { Link, useNavigate } from "react-router-dom";
import { extractApiError } from "../lib/httpErrors";

export default function ChangePassword() {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { setTokens, setUser } = useAuthStore();

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    try {
      const { data: tokens } = await api.post("/change-password", { password });
      setTokens(tokens.access, tokens.refresh);
      navigate("/users");
    } catch (err: any) {
      const parsed = extractApiError(err as unknown);
      setError(`Changing password failure: ${parsed.message}`);
    }
  }

  return (
    <div className="max-w-md mx-auto card">
      <h1 className="text-2xl font-semibold mb-4">Change Password</h1>
      <form onSubmit={onSubmit} className="space-y-3">
        <FormInput placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)} required />
        <FormInput placeholder="ConfirmPassword" type="password" value={confirmPassword} onChange={e=>setConfirmPassword(e.target.value)} required />
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <button className="btn w-full" type="submit">Sign in</button>
      </form>
      <div className="mt-4 text-sm flex justify-between">
        /* Add elements, if needed */
      </div>
    </div>
  );
}
