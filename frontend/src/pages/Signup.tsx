import { useState } from "react";
import { api } from "../lib/axios";
import FormInput from "../components/FormInput";
import { useNavigate } from "react-router-dom";
import { extractApiError } from "../lib/httpErrors";

type FieldErrors = {
  email?: string | string[];
  username?: string | string[];
  password?: string | string[];
  detail?: string | string[];
  non_field_errors?: string | string[];
};
const toText = (v?: string | string[]) =>
  Array.isArray(v) ? v.join(" ") : v ?? "";

export default function Signup() {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  // const [error, setError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const navigate = useNavigate();

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
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
      // setError("Signup failed: " + String(message) + "; fields: " + String (fields))
      // const top = "Signup failed: " + String(message) + "; fields: " + String (fields)
      // setSubmitError(top);
      setSubmitError(message || "Signup failed. Please try again.");
      if (fields) setFieldErrors(fields as FieldErrors);
    }
  }

  return (
    <div className="max-w-md mx-auto card">
      <h1 className="text-2xl font-semibold mb-4">Sign up</h1>
      <form onSubmit={onSubmit} className="space-y-3">
        <FormInput placeholder="Email" type="email" value={email} onChange={e=>setEmail(e.target.value)} required />
        {fieldErrors.email && (
          <p className="text-xs text-red-600">{toText(fieldErrors.email)}</p>
        )}
        <FormInput placeholder="Username" value={username} onChange={e=>setUsername(e.target.value)} required />
        {fieldErrors.username && (
          <p className="text-xs text-red-600">{toText(fieldErrors.username)}</p>
        )}
        <FormInput placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)} required />
        {fieldErrors.password && (
          <p className="text-xs text-red-600">{toText(fieldErrors.password)}</p>
        )}
        <button className="btn w-full" type="submit">Create account</button>
      </form>
    </div>
  );
}
