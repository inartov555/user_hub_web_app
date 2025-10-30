# Project Architecture

This repository implements a **containerised SPA** with a typed React frontend and a Django/DRF backend.

```
[ Browser SPA ]  ──HTTP──>  [ Nginx (frontend) ]  ──/api/*──>  [ Django REST API ]  ──SQL──>  [ PostgreSQL ]
       |                              |                             |
   React + TS +                       |                             |-- DRF Spectacular (OpenAPI + Swagger)
   TanStack Query                     |                             |-- Djoser + SimpleJWT (JWT auth)
   Zustand auth state                 |                             |-- Profiles app (users/profiles/settings)
```

---

## Components

### Frontend (Vite + React + TS)
- **State:** Zustand store for auth (`access`, `refresh`, `user`).
- **Data fetching:** TanStack Query with request de‑duplication, caching and retries.
- **HTTP:** Axios instance at `src/lib/axios.ts` with an **interceptor** that:
  - attaches `Authorization: Bearer <access>`,
  - decodes expiry to proactively **refresh** near `JWT_RENEW_AT_SECONDS`,
  - queues concurrent requests during an inflight refresh,
  - retries once after a successful refresh.
- **Routing & guards:** ProtectedRoute ensures authenticated access to private pages.
- **Styling:** Tailwind; UI primitives in `src/components/*`.
- **i18n:** JSON dictionaries under `src/locale/*`, initialized in `src/lib/i18n.ts`.

### Backend (Django + DRF)
- **Apps:** `core` (settings/urls), `profiles` (users, profiles, settings, import, stats).
- **Auth:** Djoser for endpoints, SimpleJWT for tokens, custom serializers to allow **email or username** login.
- **OpenAPI:** `drf-spectacular` exposes `/api/schema/` and `/api/docs/`.
- **Filtering/sorting:** `django-filter`, `OrderingFilter`, `SearchFilter` on list endpoints.
- **CORS:** `django-cors-headers` configured in settings.
- **Internationalization:** backend messages localized; language normalization middleware.

### Database
- PostgreSQL 16 (Docker). Migrations are managed by Django.

---

## Custom middleware

1) **JWT authentication middleware** (`profiles/middleware/jwt_authentication_middleware.py`)  
   Extracts access token strictly from the **Authorization header**, validates it, sets `request.user` for DRF,
   and marks requests that are close to expiry so the client can refresh. It does **not** issue new tokens.

2) **Idle timeout middleware** (`profiles/middleware/idle_timeout_middleware.py`)  
   Tracks last activity and rejects requests after `IDLE_TIMEOUT_SECONDS` of inactivity to enforce re‑auth.

3) **Last activity** (`profiles/middleware/last_activity_middle_ware.py`)  
   Records per‑user activity timestamps used by the **online users** endpoint.

4) **Boot‑ID enforcer** (`profiles/middleware/boot_id_enforcer.py`)  
   Embeds a boot epoch in tokens and rejects requests when the server boots with a **new epoch** (deploy/restart),
   forcing clients to refresh and preventing acceptance of stale tokens after redeploys.

5) **Language normalizer** (`profiles/middleware/normalize_language_middleware.py`)  
   Normalizes `Accept-Language`/query params to configured locales and activates Django translations.

---

## Auth timing & runtime settings

Runtime‑tunable values are persisted in the `AppSetting` model and merged with defaults from Django settings:

- `ACCESS_TOKEN_LIFETIME` (seconds) – DRF SimpleJWT access token TTL
- `JWT_RENEW_AT_SECONDS` – how long **before** expiry the client should refresh
- `IDLE_TIMEOUT_SECONDS` – how long of inactivity before user must re‑authenticate

Effective values are exposed at:
- `GET /api/system/settings/` (read) and `PUT /api/system/settings/` (update)
- `GET /api/system/runtime-auth/` (read‑only effective values)

The frontend periodically reads these and adjusts its interceptor thresholds.

---

## Request flow

1) SPA makes a request → Axios attaches `Authorization: Bearer <access>`.
2) Backend middleware authenticates the token and enforces boot‑id and idle timeout.
3) DRF view/serializer handles the request.
4) If a 401 is returned due to expiry, the interceptor attempts **one refresh** via `/auth/jwt/refresh/` and retries.
5) On repeated failure, the SPA clears auth state and redirects to `/login`.

---

## Internationalization (i18n)

- **Frontend:** string keys resolved by `react-i18next`; locale switcher in the UI.
- **Backend:** `gettext` for server messages; language normalized & activated by middleware.

---

## Static/media

- Frontend build produces static assets served by Nginx.
- User avatars and other uploads are served from `/media/…` (Django `MEDIA_URL`). Serializers emit absolute URLs.

---

## Observability & DX

- OpenAPI/Swagger at `/api/docs/` for quick exploration.
- Clear error responses using DRF’s standard format.
- Developer helper script: `run_web_site.sh` sets up a local workspace and launches services.

---

## Security considerations

- Short‑lived access token; refresh handled explicitly, not via cookies.
- Boot‑id invalidation to prevent token reuse across deployments.
- Strong password validation; admin‑only password reset endpoint.
- CORS restricted; Authorization header only (no token in cookies/localStorage persisted by default).
- Input validation on Excel import.

---

## Future improvements

- Rate limiting (DRF throttling) and audit logging
- E2E tests (Playwright/Cypress) + API tests (pytest + APIClient)
- Background task queue for heavy Excel imports
- S3‑backed media storage for production
