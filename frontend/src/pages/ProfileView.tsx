import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/axios";
import { useAuthStore } from "../auth/store";
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
  avatar?: string | null; // relative path, e.g. /media/avatars/...
  avatar_url?: string | null; // absolute URL if backend provides it
  user: ProfileUser;
};

export default function ProfileView() {
  const { t, i18n } = useTranslation();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const { user, logout, accessToken } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const resp = await api.get<Profile>("/me/profile/");
        if (!alive) return;
        const p = resp.data;
        setProfile(p);
        setError(null);
        setLoading(false);
      } catch (e: any) {
        if (!alive) return;
        setError(e?.response?.data?.detail || e?.message || t("profileEdit.profileLoadError"));
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  if (loading) return <div className="card p-4">{t("users.loading")}</div>;
  if (error) return <div className="card p-4 text-red-600">{t("profileView.pViewError", { message: error })}</div>;

  if (!profile)
    return (
      <div className="card p-4">
        <p className="mb-2">{t("profileView.noProfileFound")}</p>
        <Link to="/profile-edit" className="btn inline-flex">
          {t("profileView.createEditProfile")}
        </Link>
      </div>
    );

  const mediaBase = (import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1").replace(/\/api\/v1$/, "");
  const fullName =
    [profile.user?.first_name, profile.user?.last_name].filter(Boolean).join(" ") || "—";

  const initials =
    (profile.user?.first_name?.[0] || "") + (profile.user?.last_name?.[0] || "");

  // Prefer absolute avatar_url if provided
  const avatarSrc =
    profile.avatar_url ??
    (profile.avatar ? mediaBase + profile.avatar : `https://placehold.co/160x160?text=${encodeURIComponent(initials || "👤")}`);

  return (
    <div className="card grid grid-cols-1 gap-6 md:grid-cols-3 p-4 rounded-2xl border bg-white dark:bg-slate-800 dark:text-slate-100 dark:border-slate-700">
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

      {/* Right: Details */}
      <div className="md:col-span-2 space-y-4">
        <div>
          <h2 className="text-xl font-semibold">{t("profileView.profile")}</h2>
          <p className="text-sm text-slate-500">{t("profileView.yourPersonalDetails")}</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Field label={t("profileView.fullName")} value={fullName} />
          <Field label={t("signup.username")} value={profile.user?.username || "—"} />
          <Field label={t("signup.email")} value={profile.user?.email || "—"} />
          <Field label={t("profileView.pId")} value={String(profile.user?.id ?? "—")} />
        </div>

        <div>
          <Field label={t("excelImport.bio")} value={String(profile?.bio ?? "—")} />
        </div>

        <div className="pt-2">
          <Button variant="secondary" className="gap-2">
            <Link to="/profile-edit" className="btn inline-flex">
              {t("profileView.editProfile")}
            </Link>
          </Button>
          {profile?.user?.id != null && (
            <Button variant="secondary" className="gap-2">
              <Link
                to={`/users/${profile.user.id}/change-password`}
                className="btn inline-flex"
              >
                {t("profileView.changePassword")}
              </Link>
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

/* UI helpers */
function Label({ children }: { children: React.ReactNode }) {
  return <div className="text-xs font-medium text-slate-500">{children}</div>;
}
function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <Label>{label}</Label>
      <div className="
            w-full rounded-xl px-3 py-2
            bg-white text-slate-900 placeholder-slate-500
            border border-slate-300
            focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500
            dark:bg-slate-900 dark:text-slate-100 dark:placeholder-slate-500
            dark:border-slate-700
          ">
        {value}
      </div>
    </div>
  );
}
