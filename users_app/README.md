<p align="center">
  <img src="frontend/public/logo.svg" alt="Users App logo" width="80">
</p>

-----

## 💡 Users App

- A production‑grade example app with a **Django REST Framework (DRF)** backend and a **React + Vite + TypeScript** SPA frontend.
- It demonstrates JWT auth with runtime tuning, profile management, Excel import, online-user stats, i18n, and a clean Tailwind UI.
- Created on Oct-10-2025

---

## 🔑 Admin credentials (dev)
- `admin / changeme123`

## 🚀 Quick start (Docker)

**Prerequisites:** Docker & docker‑compose.

```
# You can just run ./run_website.sh, it defaults to ./run_website.sh false false false

./run_website.sh param1 param2 param3

# Input parameters:
#
#     Data clearing when exiting
#   - $1 - true - delete the DB data after stopping the service;
#          false - preserve the DB data after stopping the service;
#          default = false
#
#     Clearing cache before starting service
#   - $2 - true - starting service WITHOUT cached data (allows to start the service faster);
#          false - starting the service WITH cache (cache is cleared)
#          default = false
#
#     !!! Clearing Docker data (ALL Docker images, Docker network settings, etc.), and restarting the Docker service
#   - $3 - true - clearing all docker data (network, images, etc.)
#          false - docker starts with new data
#          default = false
```

Copied project folder, run results like logs, etc., are located in: `/home/$user_name/TEST1/workspace`. Artifacts (run results, logs, etc.) are located in: `/home/$user_name/TEST1/workspace/artifacts`.

Open:
- **API Swagger:** [http://localhost:8000/api/v1/docs/](http://localhost:8000/api/v1/docs/)
- **OpenAPI JSON:** [http://localhost:8000/api/v1/schema/](http://localhost:8000/api/v1/schema/)
- **Frontend:** [http://localhost:5173/](http://localhost:5173/)

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
|   `-- core/                # settings, urls, wsgi
|   `-- locale/              # /cs_CZ/LC_MESSAGES/django.po, etc.
|   `-- profiles/            # users, profiles, settings, import, stats
|   `-- tests/               # unit tests
|-- frontend/                # React + Vite SPA
|   `-- public/              # logo.svg
|   `-- src/
|       `-- auth/            # auth store + guards
|       `-- components/      # UI primitives
|       `-- lib/             # axios, query client, i18n, settings API
|       `-- locale/          # translations
|       `-- pages/           # screens (Login, Users, Profile, Settings, Import, Stats, ...)
|       `-- __tests__/       # unit tests
|-- docker-compose.yml
|-- run_website.sh
`-- test_data/               # *.xlsx
```

---

## ⚙️ Configuration

### Backend environment (most relevant)
- `DATABASE_URL` — Postgres DSN (`postgres://...`)
- **JWT & idle timing**
  - `ACCESS_TOKEN_LIFETIME` — seconds (e.g. `1800`)
  - `IDLE_TIMEOUT_SECONDS` — seconds (e.g. `900`)
  - `JWT_RENEW_AT_SECONDS` — seconds before expiry to silently refresh (e.g. `1200`)
  - `ROTATE_REFRESH_TOKENS` — `true|false`

### Frontend environment
- `VITE_API_URL` — base API path; defaults to `/api/v1`

---

## 🔌 API surface (high‑level)

**API documentation:** [http://localhost:5173/api/v1/docs/](http://localhost:5173/api/v1/docs/)

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

## 🛡️ Security & auth behaviour

- Password validation with Django validators
- JWTs are stored in memory on the client to reduce XSS persistence risk (no HTTP-only cookies)
- CORS locked down with `django-cors-headers`
- Boot‑ID enforcement: when the backend restarts, stale JWTs are invalidated; the frontend silently re‑auths/refreshes when possible
- Excel import and serializers include strict validation & error reporting

---

## ▶️ DEMOs

### ▶️ Light Theme. Main pages
![Light Theme. Main pages](https://github.com/inartov555/user_hub_web_app/blob/stable_v1.3_dec_28_2025/users_app/DEMO/Light%20Theme.%20Main%20pages.gif)

### ▶️ Dark Theme. Main pages
![Dark Theme. Main pages](https://github.com/inartov555/user_hub_web_app/blob/stable_v1.3_dec_28_2025/users_app/DEMO/Dark%20Theme.%20Main%20pages.gif)

### ▶️ Localization
![Localization](https://github.com/inartov555/user_hub_web_app/blob/stable_v1.3_dec_28_2025/users_app/DEMO/Localization.gif)
