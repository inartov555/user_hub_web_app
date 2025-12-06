<p align="center">
  <img src="frontend/public/logo.svg" alt="Users App logo" width="80">
</p>

-----

# 💡 Users App

- A production‑grade example app with a **Django REST Framework (DRF)** backend and a **React + Vite + TypeScript** SPA frontend.
- It demonstrates modern JWT auth with runtime tuning, profile management, Excel import, online-user stats, i18n, and a clean Tailwind UI.
- Created on Oct-10-2025

---

## ℹ️ Info

- **Users App: Stable version #1**: https://github.com/inartov555/user_hub_web_app/tree/stable_v1_nov_05_2025

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
- **Frontend:** http://localhost:5173/
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
- Access token is attached to `Authorization: Bearer <token>`. The refresh token is stored in the SPA's local storage.
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
- Middleware: idle timeout, boot ID enforcement, and auth header handling
- Permissions on all endpoints (admin vs regular user)
- i18n correctness for top locales
- Frontend: auth store transitions, interceptor logic, protected routes

---

## ⚙️ Configuration

### Backend environment (most relevant)
- `ALLOWED_HOSTS` — comma‑separated list
- `CORS_ALLOWED_ORIGINS` — comma‑separated list
- `DATABASE_URL` — Postgres DSN (`postgres://...`)
- `DJANGO_DEBUG` — `true|false`
- **JWT & idle timing**
  - `ACCESS_TOKEN_LIFETIME` — seconds (e.g. `1800`)
  - `IDLE_TIMEOUT_SECONDS` — seconds (e.g. `900`)
  - `JWT_RENEW_AT_SECONDS` — seconds before expiry to silently refresh (e.g. `1200`)
  - `ROTATE_REFRESH_TOKENS` — `true|false`
- `SPECTACULAR_SETTINGS` — OpenAPI metadata (see `core/settings.py`)

### Frontend environment
- `VITE_API_URL` — base API path; defaults to `/api/v1`

---

## 🔌 API surface (high‑level)

| Method | Path                                   | Purpose |
|-------:|----------------------------------------|---------|
| GET    | `/api/v1/users/`                       | List/search users (DRF router) |
| POST   | `/api/v1/users/`                       | Create user |
| GET    | `/api/v1/users/:id/`                   | Retrieve user |
| PUT    | `/api/v1/users/:id/`                   | Update user |
| DELETE | `/api/v1/users/:id/`                   | Delete user |
| GET    | `/api/v1/me/profile/`                  | Current user profile |
| POST   | `/api/v1/import-excel/`                | Excel import (xlsx based on template) |
| GET    | `/api/v1/stats/online-users/`          | Users active in the last 5 minutes |
| GET/PUT| `/api/v1/system/settings/`             | Read/update effective auth timings |
| GET    | `/api/v1/system/runtime-auth/`         | Read runtime‑computed auth config |
| POST   | `/api/v1/auth/jwt/create`              | Obtain access/refresh (Djoser) |
| POST   | `/api/v1/auth/jwt/refresh/`            | Refresh access (runtime‑aware) |
| GET    | `/api/v1/schema/`                      | OpenAPI schema |
| GET    | `/api/v1/docs/`                        | Swagger UI |

---

## 🧪 Unit Tests

```bash
# backend
cd backend && pytest -q

# frontend
cd frontend && npm run test
```

---

## 🛡️ Security & auth behaviour

- Strong password validation with Django validators
- JWTs are stored in memory on the client to reduce XSS persistence risk (no http‑only cookies)
- CORS locked down with `django-cors-headers`
- **Boot‑ID enforcement**: when the backend restarts, stale JWTs are invalidated; the frontend silently re‑auths/refreshes when possible
- Excel import and serializers include strict validation & error reporting

---

## ▶️ DEMOs

### ▶️ Light Theme. Main pages
![Light Theme. Main pages](https://github.com/inartov555/user_hub_web_app/blob/main/users_app/DEMO/Light%20Theme.%20Main%20pages.gif)

### ▶️ Dark Theme. Main pages
![Dark Theme. Main pages](https://github.com/inartov555/user_hub_web_app/blob/main/users_app/DEMO/Dark%20Theme.%20Main%20pages.gif)

### ▶️ Localization
![Localization](https://github.com/inartov555/user_hub_web_app/blob/main/users_app/DEMO/Localization.gif)
