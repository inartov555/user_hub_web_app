import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/axios";

export default function ProfileEdit() {
  const navigate = useNavigate();
  const [data, setData] = useState<any>(null);
  const [first_name, setFirstName] = useState("");
  const [last_name, setLastName] = useState("");
  const [bio, setBio] = useState("");
  const [avatarFile, setAvatarFile] = useState<File | null>(null);

  useEffect(() => { (async () => {
    const { data } = await api.get("/me/profile/");
    setData(data); setFirstName(data.user.first_name || ""); setLastName(data.user.last_name || ""); setBio(data.bio || "");
  })(); }, []);

  async function onSave() {
    const form = new FormData();
    form.append("first_name", first_name);
    form.append("last_name", last_name);
    form.append("bio", bio);
    if (avatarFile) form.append("avatar", avatarFile);
    const { data } = await api.patch("/me/profile/", form, { headers: { "Content-Type": "multipart/form-data" }});
    setData(data);
    navigate("/profile-view");
  }

  if (!data) return <div className="card">Loading...</div>;
  const mediaBase = (import.meta.env.VITE_API_URL ?? "http://localhost:8000/api").replace(/\/api$/, "");
  return (
    <div className="card grid grid-cols-1 md:grid-cols-3 gap-6">
      <div>
        <img className="w-40 h-40 rounded-full object-cover border" src={data.avatar ? mediaBase + data.avatar : `https://placehold.co/160x160?text=Avatar`} />
      </div>
      <div className="md:col-span-2 space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <input className="input" placeholder="First name" value={first_name} onChange={e=>setFirstName(e.target.value)} />
          <input className="input" placeholder="Last name" value={last_name} onChange={e=>setLastName(e.target.value)} />
        </div>
        <textarea className="input min-h-[120px]" placeholder="Bio" value={bio} onChange={e=>setBio(e.target.value)} />
        <input type="file" accept="image/*" onChange={(e)=>setAvatarFile(e.target.files?.[0] || null)} />
        <div className="flex gap-2">
          <button className="btn" onClick={onSave}>Save</button>
        </div>
      </div>
    </div>
  );
}
