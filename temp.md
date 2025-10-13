## This project is being developed

## Users App (Django + React)

## Setup (Docker)
```bash
cp backend/.env.example backend/.env
docker compose up --build -d
docker compose exec backend python manage.py createsuperuser
# Frontend: http://localhost:5173
# API:      http://localhost:8000/api/
# Admin:    http://localhost:8000/admin/
```

## Setup (no Docker)
1. **Backend:**
   ```bash
   cd backend
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```
2. **Frontend:**
   ```bash
   cd frontend
   npm i
   echo 'VITE_API_URL=http://localhost:8000/api' > .env.local
   npm run dev
   ```

## Auth endpoints
- `POST /api/auth/users/` — register
- `POST /api/auth/jwt/create/` — login (email+password)
- `POST /api/auth/jwt/refresh/` — refresh
- `POST /api/auth/users/reset_password/` — request reset email

## App endpoints
- `GET /api/me/profile/` `PATCH /api/me/profile/`
- `GET /api/users/` — paginated list (admin-only). Query: `page`, `page_size`, `ordering`, `search`, filters.
- `POST /api/users/import-excel/` — upload `.xlsx` with columns: `email,username,first_name,last_name,is_active,bio`
- `GET /api/stats/online-users/`

## Notes
- **Security:** For production move refresh token to HttpOnly cookie, enable CSRF, strict CORS, HTTPS.
- **Media:** Avatars under `/media/avatars/*` (served by Django in dev).
- **UI:** Tailwind with subtle glass cards and alternating table rows.
- **Sorting:** Shift-click headers for multi-column server ordering.
- **Column visibility:** Toggle chips at the bottom of the table.
