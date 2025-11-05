import { useEffect, useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/axios";
import { useAuthStore } from "../auth/store";
import FormInput from "../components/FormInput";
import Button from "../components/button";
import { extractApiError } from "../lib/httpErrors";

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

      const resp = await api.patch("/me/profile/", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setData(resp.data as Profile);
      navigate("/profile-view");
    } catch (err: any) {
      console.log("Finalee???")
      const parsed = extractApiError(err as unknown);
      setError(parsed.message || t("profileEdit.saveFailed"));
    }
  }

  if (error) return <div className="card p-4 text-red-600">{error}</div>;
  if (!data) return <div className="card p-4">{t("users.loading")}</div>;

  const mediaBase = (import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1").replace(/\/api\/v1$/, "");
  const initials =
    ((data.user.first_name?.trim()?.[0] ?? "") + (data.user.last_name?.trim()?.[0] ?? "")).toUpperCase() ||
    data.user.username?.[0]?.toUpperCase() ||
    "U";

  const avatarSrc =
    data.avatar_url ??
    (data.avatar ? mediaBase + data.avatar : `https://placehold.co/160x160?text=${encodeURIComponent(initials)}`);

  return (
    <div className="card grid grid-cols-1 md:grid-cols-3 gap-6 p-4 rounded-2xl border bg-white dark:bg-slate-800 dark:text-slate-100 dark:border-slate-700">
      {/* Left: Avatar */}
      <div className="flex items-start justify-center md:justify-start">
        <img
          id="profileAvatar"
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
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <FormInput
            id="firstName"
            placeholder={t("users.firstName")}
            value={first_name}
            maxLength={40}
            onChange={(e) => setFirstName(e.target.value)}
            className="
              w-full rounded-xl px-3 py-2
              bg-white text-slate-900 placeholder-slate-500
              border border-slate-300
              focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500
              dark:bg-slate-900 dark:text-slate-100 dark:placeholder-slate-500
              dark:border-slate-700
            "
          />
          <FormInput
            id="lastName"
            placeholder={t("users.lastName")}
            value={last_name}
            maxLength={40}
            onChange={(e) => setLastName(e.target.value)}
            className="
              w-full rounded-xl px-3 py-2
              bg-white text-slate-900 placeholder-slate-500
              border border-slate-300
              focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500
              dark:bg-slate-900 dark:text-slate-100 dark:placeholder-slate-500
              dark:border-slate-700
            "
          />
        </div>

        <label className="block space-y-1">
          <span className="
            text-sm text-slate-700 dark:text-slate-100
          ">{t("excelImport.bio")}</span>
          <textarea
            id="bio"
            className="w-full rounded-md border px-3 py-2 min-h-[120px] outline-none focus:ring
            bg-white text-slate-900 placeholder-slate-500
            border border-slate-300
            focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500
            dark:bg-slate-900 dark:text-slate-100 dark:placeholder-slate-500
            dark:border-slate-700
          "
            placeholder={t("excelImport.bio")}
            value={bio}
            maxLength={500}
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

        {error && <p className="text-red-600 text-sm whitespace-pre-line">{error}</p>}
        <div className="pt-2">
          <Button id="save" variant="secondary" className="gap-2" onClick={onSave}>{t("profileEdit.save")}</Button>
          <Button id="cancel" variant="secondary" className="gap-2">
            <Link to="/profile-view">{t("userDeleteConfirm.cancel")}</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
