import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { UserPen } from "lucide-react";
import { api } from "../lib/axios";
import { extractApiError } from "../lib/httpErrors";
import { useAuthStore } from "../auth/store";
import FormInput from "../components/FormInput";
import { Input } from "../components/input";
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
  avatar?: string | null;      // relative path, e.g. /media/avatars/...
  avatar_url?: string | null;  // absolute URL if backend provides it
  user: ProfileUser;
};

export default function ProfileEdit() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<Profile | null>(null);
  const [first_name, setFirstName] = useState("");
  const [last_name, setLastName] = useState("");
  const [bio, setBio] = useState("");
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isFailedToSave, setIsFailedToSave] = useState<boolean | null>(null);

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
      const parsed = extractApiError(err as unknown);
      setError(parsed.message);
      setIsFailedToSave(true);
    }
  }

  if (loading) return <div className="card p-4">{t("users.loading")}</div>;
  if (error && isFailedToSave) return <SimpleErrorMessage errorUi={t("profileEdit.saveFailed")} errorBackend={error} />;
  if (error && !isFailedToSave) return <SimpleErrorMessage errorUi={t("profileEdit.profileLoadError")} errorBackend={error} />;
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
    <div className="
           relative overflow-hidden
           rounded-2xl border p-4
           bg-white/75 backdrop-blur shadow-soft ring-1 ring-slate-900/5
           dark:bg-slate-900/50 dark:border-slate-700/70 dark:text-slate-100 dark:ring-white/5
         "
    >
      <div aria-hidden className="
           pointer-events-none absolute inset-x-0 top-0 h-24
           bg-gradient-to-b from-brand-500/10 via-indigo-500/6 to-transparent
           dark:from-brand-400/12 dark:via-indigo-400/8
         "
      />

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

        {/* Right: Form */}
        <div className="md:col-span-2 space-y-4">
          <UnifiedTitle
            icon={<UserPen className="h-4 w-4" />}
            title={t("profileEdit.editProfile")}
            subtitle={t("profileView.yourPersonalDetails")}
          />

          <div className="
               rounded-2xl border p-4
               bg-white/70 shadow-sm ring-1 ring-slate-900/5
               dark:bg-slate-900/40 dark:border-slate-700/70 dark:ring-white/5
             "
          >
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <FormInput
                id="firstName"
                placeholder={t("users.firstName")}
                value={first_name}
                onChange={(e) => setFirstName(e.target.value)}
              />
              <FormInput
                id="lastName"
                placeholder={t("users.lastName")}
                value={last_name}
                onChange={(e) => setLastName(e.target.value)}
              />
            </div>

            <label className="block space-y-1 mt-4">
              <span className="text-sm font-medium text-slate-700 dark:text-slate-200">
                {t("excelImport.bio")}
              </span>
              <textarea
                id="bio"
                className="
                  w-full rounded-xl px-3 py-2 min-h-[140px]
                  bg-white text-slate-900 placeholder-slate-500
                  border border-slate-200/80 shadow-sm
                  focus:outline-none focus:ring-2 focus:ring-brand-400 focus:border-brand-400
                  dark:bg-slate-950/40 dark:text-slate-100 dark:placeholder-slate-500
                  dark:border-slate-700/70
                "
                placeholder={t("excelImport.bio")}
                value={bio}
                maxLength={500}
                onChange={(e) => setBio(e.target.value)}
              />
              <div className="flex justify-end text-xs text-slate-500 dark:text-slate-400">
                {bio.length}/500
              </div>
            </label>

            <div className="mt-4">
              <div className="
                   rounded-2xl border p-3
                   bg-slate-50/60
                   dark:bg-slate-950/30 dark:border-slate-700/70
                 "
              >
                <div className="text-sm font-medium text-slate-700 dark:text-slate-200">
                  {t("profileEdit.profileAvatar")}
                </div>
                <div className="mt-2">
                  <Input
                    id="profileAvatarImage"
                    type="file"
                    accept="image/*"
                    onChange={(e) => setAvatarFile(e.target.files?.[0] || null)}
                  />
                </div>
                {avatarFile?.name && (
                  <div className="mt-2 text-xs text-slate-600 dark:text-slate-300">
                    {avatarFile.name}
                  </div>
                )}
              </div>
            </div>

            <div className="mt-5 flex flex-wrap gap-2">
              <Button id="save" onClick={onSave}>
                {t("profileEdit.save")}
              </Button>
              <Button id="cancel" onClick={() => navigate("/profile-view")}>
                {t("userDeleteConfirm.cancel")}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
