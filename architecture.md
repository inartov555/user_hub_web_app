# Project Architecture Overview

This project is a typical **3‑container single‑page application (SPA)**:  
**Frontend (Vite/React)** ↔ **Backend (Django REST Framework)** ↔ **PostgreSQL**, all orchestrated with **Docker Compose**.

---

## 📁 Project Structure

```
user_hub_web_app/
├─ docker-compose.yml
├─ backend/
│  ├─ core/                # Base Django configuration (settings, urls, wsgi)
│  └─ profiles/            # User domain + API
└─ frontend/               # Vite + React + TypeScript + Tailwind SPA
```

---

## 🐳 Infrastructure (Docker Compose)

### Services
- **db** — `postgres:16`  
  Database `usersdb`, user/password `users`, persistent volume `pgdata`.

- **backend** — built from `backend/Dockerfile`  
  Runs Django development server (`python manage.py runserver 0.0.0.0:8000`).

- **frontend** — built from `frontend/Dockerfile`  
  Runs Vite dev server on port `5173`, exposes `VITE_API_URL=http://localhost:8000/api`.

> ⚠️ Currently everything runs in **development mode**. For production, you would run Gunicorn/Uvicorn + Nginx and build the frontend statically.

---

## 🧠 Backend (Django + DRF)

### Core (`backend/core/`)

- **settings.py**
  - `INSTALLED_APPS`: `rest_framework`, `django_filters`, `corsheaders`, `djoser`, `drf_spectacular`, local `profiles`.
  - **Database**: PostgreSQL (`POSTGRES_*` env vars).
  - **CORS**: allowed origin from `FRONTEND_ORIGIN` (default `http://localhost:5173`).
  - **DRF** defaults:
    - Auth: `JWTAuthentication`
    - Permissions: `IsAuthenticated`
    - Filters: `DjangoFilterBackend`, `OrderingFilter`, `SearchFilter`
    - Schema: `drf_spectacular`
  - **JWT (SimpleJWT)**: access 15 min, refresh 7 days, rotation enabled.
  - **Djoser**: login via email, custom serializers from `profiles.serializers`.
  - **Middleware**: `profiles.middleware.LastActivityMiddleware` updates `last_activity` on each authenticated request.
  - **MEDIA**: `MEDIA_URL=/media/`, `MEDIA_ROOT=BASE_DIR/media`.

- **urls.py**
  - `/admin/`
  - `/api/schema/` and `/api/docs/` (Swagger / OpenAPI)
  - `/api/auth/` — Djoser JWT endpoints
  - `/api/` — app routes (`profiles.urls`)

---

### App: `profiles/`

#### Models
`Profile`: one‑to‑one with `User`, fields `bio`, `avatar`, `last_activity`.

#### Signals
Automatically create a `Profile` on new `User` creation (`post_save` signal).

#### Middleware
`LastActivityMiddleware` — updates `Profile.last_activity` for logged‑in users.

#### Serializers
- `UserSerializer`
- `ProfileSerializer`
- `ProfileUpdateSerializer` (writes both profile and nested user fields).

#### API Views
- `UsersViewSet(ReadOnlyModelViewSet)` — list/detail of users with filters, search, ordering, pagination.
- `MeProfileView(RetrieveUpdateAPIView)` — `GET/PATCH /api/me/profile/`, multipart upload for avatar.
- `ExcelUploadView(GenericAPIView)` — `POST /api/users/import-excel/`, bulk import/update from Excel (admin only).
- `OnlineUsersView(ListAPIView)` — `GET /api/stats/online-users/`, users active in the last 5 minutes.

#### Routing
`backend/profiles/urls.py`:
```python
router.register("users", UsersViewSet)
urlpatterns = [
    path("me/profile/", MeProfileView.as_view()),
    path("users/import-excel/", ExcelUploadView.as_view()),
    path("stats/online-users/", OnlineUsersView.as_view()),
]
```

---

### Backend Request Flow

1. **Auth**: frontend calls `/api/auth/jwt/create/` → receives `access` + `refresh`.
2. **API calls**: include `Authorization: Bearer <token>` header.
3. On 401 → frontend silently refreshes via `/api/auth/jwt/refresh/`.
4. **LastActivityMiddleware** updates `last_activity` each request.
5. **Online stats** endpoint reads recent `last_activity` values.

---

## 💻 Frontend (Vite + React + TS + Tailwind)

### Entry Points
- `src/main.tsx` — sets up Router + React Query client + styles.
- `src/App.tsx` — navbar and outlet for pages.

### State / Auth (Zustand)
`src/auth/store.ts` — stores `access`/`refresh` tokens and current `user` in localStorage.

### HTTP Client (Axios)
`src/lib/axios.ts`
- `baseURL = import.meta.env.VITE_API_URL || "http://localhost:8000/api"`.
- Interceptor adds `Authorization: Bearer` header.
- On 401: refreshes token automatically and retries request.

### React Query
`src/lib/queryClient.ts` — global QueryClient for caching and invalidation.

### Pages
- `Login`, `Signup`, `ResetPassword` — Djoser auth forms.
- `Profile` — view/update own profile (multipart avatar upload).
- `UsersTable` — admin list of users using **TanStack Table** with sorting/search/column visibility.
- `Stats` — list of online users (`/stats/online-users/`).

### Components
`Navbar`, `FormInput`, `ColumnVisibilityMenu`, etc.

### Styling
Tailwind CSS via `tailwind.config.js` + `postcss.config.js`.

---

## 🌐 API Map

| Endpoint | Method | Description |
|-----------|---------|-------------|
| `/api/auth/jwt/create/` | POST | Login |
| `/api/auth/jwt/refresh/` | POST | Refresh token |
| `/api/users/` | GET | List users (admin) |
| `/api/me/profile/` | GET/PATCH | Get or update current user's profile |
| `/api/users/import-excel/` | POST | Bulk import users (admin) |
| `/api/stats/online-users/` | GET | Online users |
| `/api/docs/` | GET | Swagger UI |
| `/api/schema/` | GET | OpenAPI spec |

---

## 🧩 File Reference

| File | Purpose |
|------|----------|
| `docker-compose.yml` | Infrastructure configuration |
| `backend/core/settings.py` | Django settings |
| `backend/core/urls.py` | Root API routing |
| `backend/profiles/views.py` | API view classes |
| `backend/profiles/serializers.py` | API serializers |
| `backend/profiles/models.py` | Database models |
| `backend/profiles/middleware.py` | Last activity tracker |
| `frontend/src/*` | React app source |
| `frontend/src/lib/axios.ts` | API client |
| `frontend/src/auth/store.ts` | Auth state |
| `frontend/tailwind.config.js` | Tailwind setup |

---

## ⚙️ Interaction Flow

1. SPA (`http://localhost:5173`) sends requests to backend (`http://localhost:8000/api`).
2. DRF authenticates via JWT and communicates with PostgreSQL.
3. Middleware + signals keep user and profile data synchronized.
4. OpenAPI/Swagger documents the API.
5. React Query handles caching and revalidation on the frontend.

---

## 🚀 Tips for Local Dev

- Ensure `VITE_API_URL` points to backend (`http://localhost:8000/api`).
- Vite must bind to `0.0.0.0` for Docker (`--host` flag).
- Add `CHOKIDAR_USEPOLLING=1` for stable file watching on Docker Desktop.

---
