## Users App (Django + React)
This is a test web application

## Setup (Docker)
```bash
./run_web_site.sh param1 param2
# admin user: admin / changeme123
#   - param1 - true - delete the DB data after stopping the service;
#              false - preserve the DB data after stopping the service;
#              default = false
#   - param2 - true - starting service WITHOUT cached data (allows to start the service faster);
#              false - starting the service WITH cache (cache is cleared)
#              default = false
# Frontend: http://localhost:5173
# API:      http://localhost:8000/api/
# Admin:    http://localhost:8000/admin/
```

---

## Auth endpoints
- `POST /api/auth/users/` — register
- `POST /api/auth/jwt/create/` — login (email+password)
- `POST /api/auth/jwt/refresh/` — refresh
- `POST /api/auth/users/reset_password/` — request reset email

---

## App endpoints
- `GET /api/me/profile/` `PATCH /api/me/profile/`
- `GET /api/users/` — paginated list (admin-only). Query: `page`, `page_size`, `ordering`, `search`, filters.
- `POST /api/users/import-excel/` — upload `.xlsx` with columns: `email,username,first_name,last_name,is_active,bio`
- `GET /api/stats/online-users/`

--

## Notes
- **Security:** For production move refresh token to HttpOnly cookie, enable CSRF, strict CORS, HTTPS.
- **Media:** Avatars under `/media/avatars/*` (served by Django in dev).
- **UI:** Tailwind with subtle glass cards and alternating table rows.
- **Sorting:** Shift-click headers for multi-column server ordering.
- **Column visibility:** Toggle chips at the bottom of the table.

---

## ⚙️ Features

### 🔐 Authentication
- **Login Page** — Allows users to sign in.  
- **Signup Page** — Enables new users to create an account.  
- **Reset Password Page** — Provides a way to reset forgotten passwords.

### 👤 User Management
- **User Profile Page** — Available for logged-in users, with the ability to update user details.  
- **Profile Image Upload** — Logged-in users can upload a profile picture.  
- **Upload via Excel** — Logged-in users can upload their details through an Excel file.

### 📊 User Table
- Displays a list of all registered users.  
- The table supports:
  - **Horizontal Scrolling** — View all columns if there are many.  
  - **Pagination** — Navigate between pages without reloading the entire web page (only the table updates).  
  - **Filtering & Sorting** — Filter and sort by one or multiple columns.

#### Table Design
- **Rows per Page:** Configurable; default is 20 rows.  
- **Column Visibility:** Users can select which columns to display (all are shown by default).

### 📈 User Statistics
- A dedicated statistics page showing currently logged-in users.

### 🎨 Design
- Clean, simple, and visually appealing layout.  
- Light background for a modern, user-friendly appearance.

---

## 💾 Data Storage
All user data is stored in a **reliable and free database** (you can choose any suitable option, such as PostgreSQL or SQLite).
