# UserHub — Django + React user management app

A full‑stack starter that includes:

- Django REST API with JWT auth
- Custom user model (+ profile image, last_seen activity)
- Excel import for profile fields
- Users table with pagination, sorting, filtering, column chooser, and variable page size
- React front end (Vite + React Router + Tailwind + TanStack Query + Axios)
- Profile page (edit + upload avatar + import from Excel)
- Login, Signup, Reset Password (change password for logged‑in user)
- Users statistics page (who's online, active counts)

## Quick start

### 1) Back end

```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The API will run on http://127.0.0.1:8000/

### 2) Front end

```bash
cd ../frontend
npm install
npm run dev
```

The app will run on http://127.0.0.1:5173/ and talks to the API at http://127.0.0.1:8000/ by default.

## Notes

- Database: SQLite by default (simple and free). To switch to Postgres, set `DATABASE_URL` in `.env` (e.g. `postgres://user:pass@localhost:5432/userhub`) and install `psycopg2-binary` on your machine.
- Password reset is implemented as an **authenticated change password** page. If you want email-based "forgot password", hook up SMTP and Django's `PasswordResetView` or a custom DRF flow.
- "Currently online" users are computed as users whose `last_seen` was updated within the last 5 minutes (updated on every authenticated API call).
- The Users table uses server-side pagination, sorting and filtering.
