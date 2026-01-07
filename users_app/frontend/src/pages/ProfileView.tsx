import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { UserCircle } from "lucide-react";
import { api } from "../lib/axios";
import { extractApiError } from "../lib/httpErrors";
import { useAuthStore } from "../auth/store";
import Button from "../components/button";
import { SimpleErrorMessage } from "../components/Alerts";
import UnifiedTitle from "../components/UnifiedTitle";

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
  const [errorLines, setErrorLines] = useState<string[]>([]);

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
      } catch (err: any) {
        const parsed = extractApiError(err as unknown);
        setError(parsed.message);
        setLoading(false);
        if (!alive) return;
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  if (loading) return <div className="card p-4">{t("users.loading")}</div>;
  if (error) return <SimpleErrorMessage errorUi={t("profileEdit.profileLoadError")} errorBackend={error} />;

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
  const bioField = profile?.bio || "—";

  const initials =
    (profile.user?.first_name?.[0] || "") + (profile.user?.last_name?.[0] || "");

  // Prefer absolute avatar_url if provided
  const avatarSrc =
    profile.avatar_url ??
    (profile.avatar ? mediaBase + profile.avatar : `https://placehold.co/160x160?text=${encodeURIComponent(initials || "👤")}`);

  return (
    <div className="
           relative overflow-hidden
           rounded-2xl border p-4
           bg-white/75 backdrop-blur shadow-soft ring-1 ring-slate-900/5
           dark:bg-slate-900/50 dark:border-slate-700/70 dark:text-slate-100 dark:ring-white/5
         "
    >
      <div aria-hidden
           className="
             pointer-events-none absolute inset-x-0 top-0 h-24
             bg-gradient-to-b from-brand-500/10 via-indigo-500/6 to-transparent
             dark:from-brand-400/12 dark:via-indigo-400/8
           "
      />
      {/* Left: Avatar */}
      <div className="relative grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left: Avatar */}
        <div className="flex items-start justify-center md:justify-start">
          <div className="
               relative
               rounded-full p-[3px]
               bg-gradient-to-br from-brand-500/35 via-indigo-500/20 to-transparent
               dark:from-brand-400/35 dark:via-indigo-400/25
             "
          >
            <img
              id="profileAvatar"
              src={avatarSrc}
              alt={t("profileEdit.profileAvatar")}
              width={160}
              height={160}
              style={{ objectFit: "cover", borderRadius: "9999px" }}
              className="
                h-40 w-40 rounded-full
                ring-1 ring-slate-900/10 shadow-card
                dark:ring-white/10
              "
            />
            <div aria-hidden className="
                 pointer-events-none absolute inset-0 rounded-full
                 shadow-[inset_0_0_0_1px_rgba(255,255,255,0.12)]
                 dark:shadow-[inset_0_0_0_1px_rgba(255,255,255,0.08)]
               "
            />
          </div>
        </div>

        {/* Right: Details */}
        <div className="md:col-span-2 space-y-4">
          <UnifiedTitle icon={<UserCircle className="h-4 w-4" />}
                        title={t("profileView.profile")}
                        subtitle={t("profileView.yourPersonalDetails")}
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Field id="fullName" label={t("profileView.fullName")} value={fullName} />
            <Field id="username" label={t("signup.username")} value={profile.user?.username || "—"} />
            <Field id="email" label={t("signup.email")} value={profile.user?.email || "—"} />
            <Field id="userid" label={t("profileView.pId")} value={String(profile.user?.id ?? "—")} />
          </div>

          <div>
            <Field id="bio" label={t("excelImport.bio")} value={bioField} />
          </div>

          {error && (<SimpleErrorMessage errorUi={t("profileView.viewFailed")} errorBackend={error} />)}
          <div className="flex gap-2">
            <Button id="editProfile" onClick={() => navigate("/profile-edit")}>
              {t("profileView.editProfile")}
            </Button>
            {profile?.user?.id != null && (
              <Button id="changePassword" onClick={() => navigate(`/users/${profile.user.id}/change-password`)}>
                {t("profileView.changePassword")}
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

/* UI helpers */

function Field({ label, value, id }: { label: string; value: string; id: string }) {
  return (
    <div className="space-y-1.5">
      <label className="text-slate-700 dark:text-slate-200">{label}</label>

      <div
        id={id}
        style={{ overflowWrap: "anywhere", wordBreak: "break-word", whiteSpace: "pre-wrap" }}
        className="
          relative w-full rounded-xl px-3 py-2
          border border-slate-200/80 bg-gradient-to-b from-white to-slate-50/60
          text-slate-900 shadow-sm
          ring-1 ring-slate-900/5
          dark:border-slate-700/70 dark:from-slate-900/70 dark:to-slate-950/40
          dark:text-slate-100 dark:ring-white/5
        "
      >
        <span
          aria-hidden="true"
          className="
            pointer-events-none absolute left-0 top-2 bottom-2 w-1 rounded-full
            bg-gradient-to-b from-brand-500/50 to-indigo-500/30
            dark:from-brand-400/40 dark:to-indigo-400/25
          "
        />
        <div className="pl-2">{value}</div>
      </div>
    </div>
  );
}

