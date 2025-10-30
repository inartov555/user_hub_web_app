import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/axios";
import { useAuthStore } from "../auth/store";
import FormInput from "../components/FormInput";
import Button from "../components/button";

type ProfileUser = {
  id: number;
  username: string;
  email: string;
  first_name?: string | null;
  last_name?: string | null;
};

type Profile = {
  id: number;
  bio?: string | null;
  avatar?: string | null;      // relative path, e.g. /media/avatars/...
  avatar_url?: string | null;  // absolute URL if backend provides it
  user: ProfileUser;
};

export default function ProfileEdit() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuthStore();

  const [data, setData] = useState<Profile | null>(null);
  const [first_name, setFirstName] = useState("");
  const [last_name, setLastName] = useState("");
  const [bio, setBio] = useState("");
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const resp = await api.get<Profile>("/me/profile/");
        if (!alive) return;
        const p = resp.data;
        setData(p);
        setFirstName(p.user.first_name ?? "");
        setLastName(p.user.last_name ?? "");
        setBio(p.bio ?? "");
      } catch (e: any) {
        setError(e?.response?.data?.detail || e?.message || "Failed to load profile");
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  async function onSave() {
    try {
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
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || t("profileEdit.saveFailed"));
    }
  }

  if (error) return <div className="card p-4 text-red-600">{error}</div>;
  if (!data) return <div className="card p-4">{t("users.loading")}</div>;

  const mediaBase = (import.meta.env.VITE_API_URL ?? "http://localhost:8000/api").replace(/\/api$/, "");
  const initials =
    ((data.user.first_name?.trim()?.[0] ?? "") + (data.user.last_name?.trim()?.[0] ?? "")).toUpperCase() ||
    data.user.username?.[0]?.toUpperCase() ||
    "U";

  const avatarSrc =
    data.avatar_url ??
    (data.avatar ? mediaBase + data.avatar : `https://placehold.co/160x160?text=${encodeURIComponent(initials)}`);

  return (
    <div className="card grid grid-cols-1 md:grid-cols-3 gap-6 p-4 rounded-2xl border bg-white">
      {/* Left: Avatar */}
      <div className="flex items-start justify-center md:justify-start">
        <img
          src={avatarSrc}
          alt={t("profileEdit.profileAvatar")}
          width={160}
          height={160}
          style={{ objectFit: "cover", borderRadius: "50%" }}
        />
      </div>

      {/* Right: Form */}
      <div className="md:col-span-2 space-y-3">
        <div>
          <h2 className="text-xl font-semibold">{t("profileEdit.editProfile")}</h2>
          <p className="text-sm text-slate-500">{t("profileView.yourPersonalDetails")}</p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <FormInput
            placeholder={t("users.firstName")}
            value={first_name}
            onChange={(e) => setFirstName(e.target.value)}
          />
          <FormInput
            placeholder={t("users.lastName")}
            value={last_name}
            onChange={(e) => setLastName(e.target.value)}
          />
        </div>

        <label className="block space-y-1">
          <span className="text-sm text-slate-700">{t("excelImport.bio")}</span>
          <textarea
            className="w-full rounded-md border px-3 py-2 min-h-[120px] outline-none focus:ring"
            placeholder={t("excelImport.bio")}
            value={bio}
            onChange={(e) => setBio(e.target.value)}
          />
        </label>

        <div>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setAvatarFile(e.target.files?.[0] || null)}
          />
        </div>

        <div className="pt-2">
          <Button variant="secondary" className="gap-2" onClick={onSave}>{t("profileEdit.save")}</Button>
        </div>
      </div>
    </div>
  );
}
