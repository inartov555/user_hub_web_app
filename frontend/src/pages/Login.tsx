import { useState } from "react";
import { api } from "../lib/axios";
import { useAuthStore } from "../auth/store";
import FormInput from "../components/FormInput";
import { Link, useNavigate } from "react-router-dom";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { setTokens, setUser } = useAuthStore();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      const { data: tokens } = await api.post("/auth/jwt/create/", { email, password });
      setTokens(tokens.access, tokens.refresh);
      const { data: me } = await api.get("/auth/users/me/");
      setUser(me);
      navigate("/users");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Login failed");
    }
  }

  return (
    <div className="max-w-md mx-auto card">
      <h1 className="text-2xl font-semibold mb-4">Login</h1>
      <form onSubmit={onSubmit} className="space-y-3">
        <FormInput placeholder="Email" type="email" value={email} onChange={e=>setEmail(e.target.value)} required />
        <FormInput placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)} required />
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <button className="btn w-full" type="submit">Sign in</button>
      </form>
      <div className="mt-4 text-sm flex justify-between">
        <Link to="/signup">Create an account</Link>
        <Link to="/reset-password">Forgot password?</Link>
      </div>
    </div>
  );
}
