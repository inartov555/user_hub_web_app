<p align="center">
  <img src="frontend/public/logo.svg" alt="Users App logo" width="80">
</p>

-----

## 💡 Users App

- A production‑grade example app with a **Django REST Framework (DRF)** backend and a **React + Vite + TypeScript** SPA frontend.
- It demonstrates modern JWT auth with runtime tuning, profile management, Excel import, online-user stats, i18n, and a clean Tailwind UI.
- Created on Oct-10-2025

---

## 🔑 Admin credentials (dev)
- `admin / changeme123`

## 🚀 Quick start (Docker)

**Prereqs:** Docker & docker‑compose.

```
# You can just run ./run_web_site.sh, it defaults to ./run_web_site.sh false false false

./run_web_site.sh param1 param2 param3

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
#     Clearing Docker data and restarting the Docker service
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

**API documentation:** [http://localhost:5173/api/v1/docs/](http://localhost:5173/api/v1/docs/)

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
