import { useState } from "react";
import { api } from "../lib/axios";
import FormInput from "../components/FormInput";
import { useNavigate } from "react-router-dom";
import { extractApiError } from "../lib/httpErrors";

export default function Signup() {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.post("/auth/users/", {
        email: form.email,
        username: form.username || form.email.split("@")[0], // if you derive username
        password: form.password,
      });
      navigate("/login");
    } catch (err: any) {
      const { message, fields } = extractApiError(err);
      setSubmitError("Signup failed: " + message);
      if (fields) setFieldErrors("Signup failed: " + fields);
    }
  }

  return (
    <div className="max-w-md mx-auto card">
      <h1 className="text-2xl font-semibold mb-4">Sign up</h1>
      <form onSubmit={onSubmit} className="space-y-3">
        <FormInput placeholder="Email" type="email" value={email} onChange={e=>setEmail(e.target.value)} required />
        <FormInput placeholder="Username" value={username} onChange={e=>setUsername(e.target.value)} required />
        <FormInput placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)} required />
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <button className="btn w-full" type="submit">Create account</button>
      </form>
    </div>
  );
}
