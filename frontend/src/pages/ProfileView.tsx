import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/axios";

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
  avatar?: string | null;       // relative path, e.g. /media/avatars/...
  avatar_url?: string | null;   // absolute URL if backend provides it
  user: ProfileUser;
};

export default function ProfileView() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const resp = await api.get<Profile>("/me/profile/");
        if (!alive) return;
        setProfile(resp.data);
        setError(null);
      } catch (e: any) {
        if (!alive) return;
        const status = e?.response?.status;
        const msg =
          status === 401
            ? "You are not signed in."
            : status === 403
            ? "You do not have permission to view this profile."
            : e?.response?.data?.detail || e?.message || "Failed to load profile.";
        setError(msg);
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  if (loading) return <div className="card p-4">Loading…</div>;
  if (error) return <div className="card p-4 text-red-600">Error: {error}</div>;

  if (!profile)
    return (
      <div className="card p-4">
        <p className="mb-2">No profile found.</p>
        <Link to="/profile-edit" className="btn inline-flex">
          Create / edit profile
        </Link>
      </div>
    );

  const mediaBase = (import.meta.env.VITE_API_URL ?? "http://localhost:8000/api").replace(/\/api$/, "");
  const fullName =
    [profile.user?.first_name, profile.user?.last_name].filter(Boolean).join(" ") || "—";

  const initials =
    (profile.user?.first_name?.[0] || "") + (profile.user?.last_name?.[0] || "");

  // ✅ FIX: Prefer absolute avatar_url if provided
  const avatarSrc =
    profile.avatar_url ??
    (profile.avatar ? mediaBase + profile.avatar : `https://placehold.co/160x160?text=${encodeURIComponent(initials || "👤")}`);

  return (
    <div className="card grid grid-cols-1 gap-6 md:grid-cols-3 p-4 rounded-2xl border bg-white">
      {/* Left: Avatar */}
      <div className="flex items-start justify-center md:justify-start">
        <img
          src={avatarSrc}
          alt="Profile avatar"
          width={160}
          height={160}
          style={{ objectFit: "cover", borderRadius: "50%" }}
        />
      </div>

      {/* Right: Details */}
      <div className="md:col-span-2 space-y-4">
        <div>
          <h2 className="text-xl font-semibold">Profile</h2>
          <p className="text-sm text-slate-500">Your personal details</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Field label="Full name" value={fullName} />
          <Field label="Username" value={profile.user?.username || "—"} />
          <Field label="Email" value={profile.user?.email || "—"} />
          <Field label="ID" value={String(profile.user?.id ?? "—")} />
        </div>

        <div>
          <Label>Bio</Label>
          <p className="mt-1 whitespace-pre-wrap text-slate-800">
            {profile.bio?.trim() ? profile.bio : "—"}
          </p>
        </div>

        <div className="pt-2">
          <Link to="/profile-edit" className="btn inline-flex">
            Edit profile
          </Link>
          {profile?.user?.id != null && (
            <Link
              to={`/users/${profile.user.id}/change-password`}
              className="btn inline-flex"
            >
              Change password
            </Link>
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
      <div className="mt-1 rounded-md border bg-slate-50 px-3 py-2 text-slate-900">
        {value}
      </div>
    </div>
  );
}
