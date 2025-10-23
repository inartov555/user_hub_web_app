import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/axios";
import { useAuthStore } from "../auth/store";

type Profile = {
  id: number;
  bio?: string | null;
  avatar?: string | null; // e.g. /media/avatars/...
  avatar_url?: string | null; // absolute URL (if backend provides it)
  user: {
    id: number;
    username: string;
    email: string;
    first_name?: string | null;
    last_name?: string | null;
  };
};

export default function ProfileEdit() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [data, setData] = useState<Profile | null>(null);
  const [first_name, setFirstName] = useState("");
  const [last_name, setLastName] = useState("");
  const [bio, setBio] = useState("");
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user && location.pathname !== "/login") {
      navigate("/login", { replace: true, state: { from: location } });
    }
  }, [user, location, navigate]);

  async function onSave() {
    const form = new FormData();
    form.append("first_name", first_name);
    form.append("last_name", last_name);
    form.append("bio", bio);
    if (avatarFile) form.append("avatar", avatarFile);

    const resp = await api.patch<Profile>("/me/profile/", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    setData(resp.data);
    navigate("/profile-view");
  }

  if (error) return <div className="card p-4 text-red-600">{error}</div>;
  if (!data) return <div className="card">Loading...</div>;

  const mediaBase = (import.meta.env.VITE_API_URL ?? "http://localhost:8000/api").replace(/\/api$/, "");
  const initials =
    (
      (data.user.first_name?.trim()?.[0] ?? "") +
      (data.user.last_name?.trim()?.[0] ?? "")
    ).toUpperCase() ||
    data.user.username?.[0]?.toUpperCase() ||
    "U";

  const avatarSrc =
    data.avatar_url ??
    (data.avatar ? mediaBase + data.avatar : `https://placehold.co/160x160?text=${encodeURIComponent(initials)}`);

  return (
    <div className="card grid grid-cols-1 md:grid-cols-3 gap-6">
      <div>
        <img
          className="w-40 h-40 rounded-full object-cover border"
          src={avatarSrc}
          alt="Profile avatar"
          width={160}
          height={160}
        />
      </div>

      <div className="md:col-span-2 space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <input
            className="input"
            placeholder="First name"
            value={first_name}
            onChange={(e) => setFirstName(e.target.value)}
          />
          <input
            className="input"
            placeholder="Last name"
            value={last_name}
            onChange={(e) => setLastName(e.target.value)}
          />
        </div>

        <textarea
          className="input min-h-[120px]"
          placeholder="Bio"
          value={bio}
          onChange={(e) => setBio(e.target.value)}
        />
        <input type="file" accept="image/*" onChange={(e) => setAvatarFile(e.target.files?.[0] || null)} />

        <div className="flex gap-2">
          <button className="btn" onClick={onSave}>Save</button>
        </div>
      </div>
    </div>
  );
}
