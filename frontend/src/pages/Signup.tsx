import { useState } from "react";
import { api } from "../lib/axios";
import FormInput from "../components/FormInput";
import { useNavigate } from "react-router-dom";
import { extractApiError } from "../lib/httpErrors";

type FieldErrors = {
  email?: string;
  username?: string;
  password?: string;
  detail?: string;
};

export default function Signup() {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const navigate = useNavigate();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitError(null);
    setFieldErrors({});
    try {
      await api.post("/auth/users/", {
        email,
        username,
        password,
      });
      // Optionally clear the form:
      // const formEl = e.currentTarget;
      // formEl.reset();
      navigate("/login");
    } catch (err: any) {
      const { message, fields } = extractApiError(err);
      // setSubmitError(message); // overrides the error field and makes it empty
      // if (fields) setFieldErrors(fields); // overrides the error field and makes it empty
      setError("Signup failed: " + String(message) + "; fields: " + String (fields))
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
