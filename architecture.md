## Project Architecture Overview

This repository implements a **3‑service, containerised SPA**:

```
[ Browser SPA ]  ──HTTP──>  [ Nginx (frontend) ]  ──/api/*──>  [ Django REST API ]  ──SQL──>  [ PostgreSQL ]
       |                              |                             |
   React + TS +                       |                             |-- DRF Spectacular (OpenAPI)
   TanStack Query                     |                             |-- Djoser + SimpleJWT (JWT auth)
   Zustand auth state                 |                             |-- Profiles app (users/profiles)
```

- **Frontend**: Vite + React + TypeScript + Tailwind, built into static assets and served by **Nginx**.  
  Nginx proxies `/api/` to the backend container; all other routes serve the SPA (`index.html`) to support refresh/deep links.
- **Backend**: Django 5 + DRF + Djoser + **SimpleJWT**, plus the `profiles` domain app.  
  Two custom middlewares were added recently:
  - `LastActivityMiddleware` – updates `profile.last_activity` for each authenticated request.
  - `JWTAuthenticationMiddleware` – _stateless_ header‑based auth; extracts/validates **Access** tokens from `Authorization: Bearer …`.  
    It does **not** manage cookies; refresh is performed via the `/api/auth/jwt/refresh/` endpoint from the client.
- **Database**: PostgreSQL 16 with a named Docker volume (`pgdata`) for persistence.

---

## Top‑Level Layout

```
user_hub_web_app/
├─ docker-compose.yml
├─ backend/
│  ├─ core/               # Django project (settings, urls, wsgi)
│  └─ profiles/           # Users/Profile domain, serializers, views, middleware
└─ frontend/              # Vite React app, built and served by Nginx
```

### Containers & Ports

| Service     | Image/Build                     | Port (host→container) | Notes |
|-------------|----------------------------------|-----------------------|------|
| `db`        | `postgres:16`                   | `5432 → 5432`         | Database `usersdb` |
| `backend`   | `python:3.12-slim` (multi‑stage) | `8000 → 8000`         | Runs `python manage.py runserver 0.0.0.0:8000` (swap to Gunicorn for prod) |
| `frontend`  | build with Node 20 → `nginx:1.27` | `5173 → 80`           | Serves SPA and proxies `/api/` to `backend:8000` |

**Nginx proxy rule (excerpt):**
```nginx
location /api/ { proxy_pass http://backend:8000/api/; }
location /      { try_files $uri /index.html; }  # SPA fallback
```

---

## Backend Details

- **Auth**: Djoser + SimpleJWT
  - `POST /api/auth/jwt/create/` → obtain **access**/**refresh** tokens
  - `POST /api/auth/jwt/refresh/` → obtain a new **access** token (optionally rotate refresh depending on settings)
- **Schema/Docs**: DRF Spectacular
  - `GET /api/schema/` (OpenAPI 3) and `GET /api/docs/` (Swagger UI)
- **Profiles app**:
  - `GET /api/users/` … standard CRUD via `UsersViewSet`
  - `GET /api/me/profile/` … current user profile
  - `GET /api/stats/online-users/` … users active within last **5 minutes** (uses `profile.last_activity`)
  - `POST /api/import-excel/` … **bulk upsert** users & profiles from an uploaded Excel file
- **Middleware**:
  - `profiles.middleware.LastActivityMiddleware` – sets `Profile.last_activity = timezone.now()` after a successful authenticated request.
  - `profiles.middleware.JWTAuthenticationMiddleware` – validates access tokens from headers; sets `request.user`; may expose `request.new_access_token` when nearing expiry (client still refreshes via API).
- **Logging**:
  - JSON config at `profiles/tools/logger/logging.json`. Root logger writes to a file handler; app logger name: `utaf`.

> Note: No Celery/Redis queue is used. Excel import runs within the request (synchronous).

---

## Frontend Details

- **Stack**: React + TypeScript, TailwindCSS, TanStack Query, React Router, Zustand.
- **Base URL**: `VITE_API_URL` (Docker build ARG & env) – defaults to `/api`.
- **Auth flow**:
  1. User logs in via Djoser (`/api/auth/jwt/create/`).
  2. Access token is attached in `Authorization: Bearer <token>`.
  3. An Axios **response interceptor** handles `401` with `token_not_valid` by calling `/api/auth/jwt/refresh/` once, then retries the original request.  
     If refresh fails, it clears Zustand auth state and navigates to `/login`.
- **Online users UI**: `/stats` calls `/stats/online-users/` and lists users with activity in last 5 minutes.

---

## Environment & Configuration

### Backend `.env` (see `backend/.env.example`)
- `DEBUG=1`
- Database connection envs (`POSTGRES_*`) are supplied by Compose networking.
- SimpleJWT behaviour (expiry/rotation/blacklisting) is configured in `core/settings.py` via `SIMPLE_JWT` dict.
- Static/media settings are standard; media is served in DEBUG only.

### Frontend build ARGs / env
- `VITE_API_URL` (ex: `http://localhost:8000/api` in local‑non‑proxy setups).  
  In Docker, Nginx proxies `/api/` so `VITE_API_URL` can remain `/api`.

---

## Local Development

- **Docker (recommended)**
  - `./run_web_site.sh [delete_db=true|false] [no_cache=true|false]`
  - Containers:
    - Postgres with volume `pgdata`
    - Backend served on `http://localhost:8000`
    - Frontend+Nginx on `http://localhost:5173`
- **Non‑Docker**
  - Backend: create venv, `pip install -r backend/requirements.txt`, `python backend/manage.py runserver`.
  - Frontend: `npm i` then `npm run dev` (ensure `VITE_API_URL=http://localhost:8000/api`).

---

## Security Notes

- Pure **header‑based JWT**; no auth cookies. CORS allowed origins must be configured if serving frontend from a different origin.
- Refresh rotation/blacklisting is supported if `token_blacklist` app is enabled; current setup keeps refresh explicit on client.
- Nginx only proxies `/api/` to the backend; static SPA assets are immutable‑cached under `/assets/`.

---

## Known Limitations / Next Steps

- Switch backend command to **Gunicorn** for production.
- Add unit/integration tests for Excel import and JWT middleware.
- Consider rate‑limiting and stricter CORS in production.
- Add health/readiness endpoints for backend & Nginx.
