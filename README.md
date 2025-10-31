# 👥 Users App

A production‑grade example web application with a **Django REST Framework (DRF)** backend and a **React + Vite + TypeScript** SPA frontend.  
It demonstrates modern JWT auth, profile management, Excel import, online‑users stats, runtime‑tunable auth timing, i18n, and a polished UI built with Tailwind.

---

## 🚀 Quick start (Docker)

**Prereqs:** Docker & docker‑compose.

```
./run_web_site.sh param1 param2
#
#   - param1 - true - delete the DB data after stopping the service;
#              false - preserve the DB data after stopping the service;
#              default = false
#   - param2 - true - starting service WITHOUT cached data (cache is cleared);
#              false - starting the service WITH cache (allows to start the service faster);
#              default = false
```

Open:
- **API Swagger:** http://localhost:8000/api/v1/docs/
- **OpenAPI JSON:** http://localhost:8000/api/v1/schema/
- **Frontend:** depends on your setup (Nginx or `npm run dev`); see below.

---

## 🔑 Admin credentials (dev)
- admin / changeme123

---

## ✨ Features

- **JWT auth** via SimpleJWT + Djoser (login by **email or username**)
- **Users & Profiles**
  - List/filter/sort/search users (server‑side)
  - View/edit own profile, change password
  - Admin password reset for a user
- **Excel import** of users
- **Runtime auth settings**: change `ACCESS_TOKEN_LIFETIME`, `JWT_RENEW_AT_SECONDS`, `IDLE_TIMEOUT_SECONDS` via API/UI
- **Online users** snapshot (last 5 minutes of activity)
- **i18n**: multiple locales on frontend & backend
- **Typed frontend** (React + TS) with TanStack Query & Zustand
- **OpenAPI schema & Swagger UI** (DRF Spectacular)
- **Dockerized**: Postgres, API, frontend (Nginx)

---

## 🧰 Tech Stack

- **Backend:** Django, DRF, DRF‑Spectacular, Djoser, SimpleJWT, django‑filters, django‑cors‑headers
- **Frontend:** React, Vite, TypeScript, TanStack Query, Zustand, Tailwind, Lucide Icons
- **DB:** PostgreSQL 16
- **Container orchestration:** docker‑compose
- **Docs/Dev tooling:** Swagger UI at `/api/v1/docs/`, OpenAPI at `/api/v1/schema/`

---

## 🗂️ Repository layout

```
user_hub_web_app/
|-- backend/                 # Django project
|   |-- core/                # settings, urls, wsgi
|   `-- profiles/            # users, profiles, settings, import, stats
|-- frontend/                # React + Vite SPA
|   `-- src/
|       |-- auth/            # auth store + guards
|       |-- lib/             # axios, query client, i18n, settings API
|       |-- components/      # UI primitives
|       |-- pages/           # screens (Login, Users, Profile, Settings, Import, Stats, ...)
|       `-- locale/          # translations
|-- docker-compose.yml
|-- run_web_site.sh
`-- test_data/import_template_EXAMPLE.xlsx
```

---

## 🔐 Authentication

- Login via `POST /api/v1/auth/jwt/create/` with either **email** or **username** + password.
- Access token is attached to `Authorization: Bearer <token>`. Refresh token is stored in memory in the SPA store.
- Axios interceptor performs **token refresh** at 401/near‑expiry and retries the original request.
- **Idle timeout & renew‑at** thresholds are enforced by custom middleware; see **Architecture** for details.

---

## 🌍 Internationalization

- Frontend locales under `frontend/src/locale/*.json`
- Backend localized messages under `backend/locale/<lang>/`
- Browser language is normalized by `normalize_language_middleware`.

---

## 📦 Excel import

Endpoint: `POST /api/v1/import-excel/` with a file named `file` (multipart).  
Use the example file at `test_data/import_template_EXAMPLE.xlsx` as a template.

---

## 🧪 Testing ideas (not exhaustive)

- Serializer validation for password change & user creation
- Excel import happy/edge paths
- Middleware: idle timeout, boot id enforcement, auth header handling
- Permissions on all endpoints (admin vs regular user)
- i18n correctness for top locales
- Frontend: auth store transitions, interceptor logic, protected routes

---

## ⚙️ Environment variables (common)

**Backend (see `backend/.env.example` for full list):**
- `SECRET_KEY`
- `DEBUG` (default `True` for dev)
- `ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `DATABASE_URL` or `POSTGRES_*` via docker‑compose
- `ACCESS_TOKEN_LIFETIME` (seconds), `IDLE_TIMEOUT_SECONDS`, `JWT_RENEW_AT_SECONDS` (defaults in settings)

**Frontend:**
- `VITE_API_URL` (default `/api/v1`)

---

## 🔒 Security notes

- Strong password validation via Django validators
- HTTP‑only cookies are **not** used for JWT; tokens live in memory to reduce XSS persistence risk
- CORS restricted via `django‑cors‑headers`
- On backend boot/redeploy, **boot‑id enforcement** invalidates stale JWTs to force refresh
- Input validation on Excel import & DRF serializers

---

## 🧭 Troubleshooting

- **401 after deploy:** expected if boot‑id changed; the SPA should refresh tokens automatically.
- **CORS error in browser:** verify `CORS_ALLOWED_ORIGINS` and `VITE_API_URL`.
- **Import fails:** verify Excel columns match the template and server logs for row‑level errors.
