## API Reference

> **Base URL**
>
> The frontend talks to the backend via Axios with `baseURL = import.meta.env.VITE_API_URL` (defaulting to `/api` during local dev).  
> In this README, all paths are shown **relative to** `/api` (so `/auth/jwt/create/` really means `https://<host>/api/auth/jwt/create/`).

---

## API Overview (Quick Tables)

🔐 **Auth (Djoser + JWT)**
| Method | Endpoint                       | Description                                      |
|-------:|--------------------------------|--------------------------------------------------|
| POST   | /api/auth/jwt/create/          | Obtain access and refresh tokens                 |
| POST   | /api/auth/jwt/refresh/         | Refresh access token (used by Axios interceptor) |
| GET    | /api/auth/users/me/            | Get current user info                            |
| POST   | /api/auth/users/               | Sign up a new user                               |
| POST   | /api/auth/users/reset_password/| Request password reset                           |

👤 **Profile (Current User)**
| Method | Endpoint            | Description                                         |
|-------:|---------------------|-----------------------------------------------------|
| GET    | /api/me/profile/    | Fetch own profile                                   |
| PATCH  | /api/me/profile/    | Update own profile (supports multipart for avatar)  |

👥 **Users (Admin-Facing)**
| Method | Endpoint                     | Description                    |
|-------:|------------------------------|--------------------------------|
| GET    | /api/users/                  | List users (paginated, sortable)|
| DELETE | /api/users/{id}/             | Delete a single user           |
| POST   | /api/users/bulk-delete/      | Delete multiple users          |
| POST   | /api/users/{id}/set-password/| Set a user’s password          |

📊 **Excel Import (Admin)**
| Method | Endpoint               | Description                                     |
|-------:|------------------------|-------------------------------------------------|
| GET    | /api/import-excel/     | Download the Excel template                     |
| POST   | /api/import-excel/     | Upload Excel to create/update users (multipart) |

📈 **Stats**
| Method | Endpoint                   | Description                  |
|-------:|----------------------------|------------------------------|
| GET    | /api/stats/online-users/   | Retrieve online users metric |

🧩 **Developer Utilities**
| Method | Endpoint       | Description    |
|-------:|----------------|----------------|
| GET    | /api/schema/   | OpenAPI schema |
| GET    | /api/docs/     | Swagger UI     |

---

## Auth (Djoser + SimpleJWT)

### Create access/refresh tokens (login)
**URL:** `/auth/jwt/create/`  
**Method:** `POST`  
**Headers:** `Content-Type: application/json`  
**Body (JSON):**
```json
{
  "email": "user@example.com",
  "password": "string"
}
```
> Login is configured to accept **email** or **username** via a custom serializer.

**Success (200):**
```json
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token"
}
```
**Failure (400 / 401):**
```json
{ "detail": "No active account found with the given credentials" }
```
**Used for:** Signing in users from the login screen.

---

### Refresh (and rotate) tokens
**URL:** `/auth/jwt/refresh/`  
**Method:** `POST`  
**Headers:** `Content-Type: application/json`  
**Body (JSON):**
```json
{ "refresh": "jwt_refresh_token" }
```
**Success (200):**
```json
{ "access": "new_access_token" }
```
**Failure (401/403):**
```json
{ "detail": "Token is invalid or expired" }
```
**Used for:** Axios interceptor / auto-refresh near expiry.

---

### Get current user (“me”)
**URL:** `/auth/users/me/`  
**Method:** `GET`  
**Headers:** `Authorization: Bearer <access>`  
**Success (200):**
```json
{
  "id": 1,
  "username": "jdoe",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "date_joined": "2025-10-10T12:34:56Z",
  "is_active": true,
  "is_staff": false,
  "is_superuser": false
}
```
**Used for:** Bootstrapping auth state after reload.

---

### Sign up (create account)
**URL:** `/auth/users/`  
**Method:** `POST`  
**Headers:** `Content-Type: application/json`  
**Body (JSON):**
```json
{
  "email": "user@example.com",
  "username": "jdoe",
  "password": "YourPassword123!"
}
```
**Success (201):**
```json
{
  "id": 3,
  "email": "user@example.com",
  "username": "jdoe"
}
```
**Validation error (400):**
```json
{ "email": ["user with this email already exists."] }
```
**Used for:** User self-registration.

---

### Request password reset email
**URL:** `/auth/users/reset_password/`  
**Method:** `POST`  
**Headers:** `Content-Type: application/json`  
**Body (JSON):**
```json
{ "email": "user@example.com" }
```
**Success (204/200):** empty body  
**Used for:** Password reset flow (emails are sent to console in dev).

---

## Users (DRF ViewSet + custom actions)

**Router base:** `/users/` (paginated list/retrieve). Supports search, filters, and ordering.

### List users (paginated)
**URL:** `/users/`  
**Method:** `GET`  
**Headers:** `Authorization: Bearer <access>`  
**Query params:**
- `page`: number (default 1)
- `page_size`: number (default 20, max 200)
- `search`: string (matches `username`, `email`, `first_name`, `last_name`)
- `ordering`: comma-separated fields (`id,username,email,first_name,last_name,date_joined`; prefix `-` for desc)
- Filters (exact): `is_active`, `date_joined`

**Success (200):**
```json
{
  "count": 123,
  "next": "https://.../users/?page=3",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "jdoe",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "date_joined": "2025-10-10T12:34:56Z",
      "is_active": true,
      "is_staff": false,
      "is_superuser": false
    }
  ]
}
```
**Used for:** Admin users table.

---

### Retrieve a user
**URL:** `/users/{id}/`  
**Method:** `GET`  
**Headers:** `Authorization: Bearer <access>`  
**Success (200):** Same shape as a single item in `results` above.  
**Used for:** Detail drawer/view (if needed).

---

### Bulk delete users (custom action)
**URL:** `/users/bulk-delete/`  
**Method:** `POST`  
**Headers:** `Authorization: Bearer <access>`, `Content-Type: application/json`  
**Body (JSON):**
```json
{ "ids": [3, 4, 5] }
```
**Success (200):**
```json
{ "deleted": 3 }
```
**Failure (400):**
```json
{ "detail": "ids must be a list of integers" }
```
**Used for:** Deleting multiple selected users.

---

### Delete a single user (custom action)
**URL:** `/users/{id}/delete-user/`  
**Method:** `DELETE`  
**Headers:** `Authorization: Bearer <access>`  
**Success (204):** empty body  
**Failure (400):**
```json
{ "detail": "Cannot delete current user." }
```
**Used for:** Remove a single user by id.

---

### Set (change) a user’s password (custom action)
**URL:** `/users/{id}/set-password/`  
**Method:** `POST`  
**Headers:** `Authorization: Bearer <access>`, `Content-Type: application/json`  
**Body (JSON):**
```json
{ "password": "NewStrongPassword123!" }
```
**Success (200):**
```json
{ "detail": "Password updated." }
```
**Validation error (400):**
```json
{ "detail": "['This password is too short. It must contain at least 8 characters.']" }
```
**Used for:** Admin resets of user passwords or self-change via UI.

---

## Current user profile (“me”)

### Get my profile
**URL:** `/me/profile/`  
**Method:** `GET`  
**Headers:** `Authorization: Bearer <access>`  
**Success (200):**
```json
{
  "user": {
    "id": 1,
    "username": "jdoe",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2025-10-10T12:34:56Z",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false
  },
  "bio": "Hi there",
  "avatar": "/media/avatars/u_1/abcd-1234.png",
  "avatar_url": "https://<host>/media/avatars/u_1/abcd-1234.png",
  "updated_at": "2025-10-11T09:00:00Z",
  "last_activity": "2025-10-26T10:05:00Z"
}
```
**Used for:** Profile view page.

---

### Update my profile (text fields and/or avatar)
**URL:** `/me/profile/`  
**Method:** `PUT` or `PATCH`  
**Headers:** `Authorization: Bearer <access>`, `Content-Type: multipart/form-data`  
**Body (multipart form-data):**
- `bio`: string (optional)
- `avatar`: file (optional)
- `user.first_name`: string (optional)
- `user.last_name`: string (optional)

**Success (200):** Updated profile object (same shape as GET).  
**Used for:** Profile edit/save page.

---

## Excel import (bulk create/update)

### Download Excel template (current users pre-filled)
**URL:** `/import-excel/`  
**Method:** `GET`  
**Headers:** *(none required)* (allowed for anonymous; helpful for getting the template)  
**Success (200):** Binary `.xlsx` with columns: `email, username, first_name, last_name, bio` (attachment via `Content-Disposition`).  
**Used for:** “Download template” in the import panel.

---

### Upload filled Excel to create/update users
**URL:** `/import-excel/`  
**Method:** `POST`  
**Headers:** `Authorization: Bearer <access>`, `Content-Type: multipart/form-data`  
**Body (multipart form-data):**
- `file`: *Excel file* (`.xlsx`) with columns like: `email, username, first_name, last_name, is_active, bio`

**Success (200):**
```json
{ "created": 5, "updated": 12 }
```
**Failure (400):**
```json
{ "detail": "No file provided" }
```
**Used for:** Admin Excel import panel.

---

## Stats

### List currently online users (last 5 minutes)
**URL:** `/stats/online-users/`  
**Method:** `GET`  
**Headers:** `Authorization: Bearer <access>`  
**Success (200):**
```json
[
  {
    "id": 1,
    "username": "jdoe",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2025-10-10T12:34:56Z",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false
  }
]
```
**Used for:** “Currently online users” widget.

---

## API schema & docs (for devs)

### OpenAPI schema
**URL:** `/schema/`  
**Method:** `GET`  
**Headers:** *(none required)*  
**Success (200):** OpenAPI JSON

### Swagger UI
**URL:** `/docs/`  
**Method:** `GET`  
**Headers:** *(none required)*  
**Success (200):** HTML UI

---

## Common Headers & Auth

- **Authorization:** `Bearer <access>` — required for all protected endpoints.  
- **Content-Type:**  
  - `application/json` for JSON bodies.  
  - `multipart/form-data` for file uploads (profile avatar, Excel import).  
- **Accept:** The default is fine; browsers will handle file downloads automatically.

---

## Pagination, Filtering, Search (Users list)

- **Pagination:** `page`, `page_size` (default 20, max 200).  
- **Search:** `search=<term>` (matches `username`, `email`, `first_name`, `last_name`).  
- **Ordering:** `ordering=<field>` or `ordering=-<field>`; allowed: `id,username,email,first_name,last_name,date_joined`.  
- **Filters:** `is_active=<true|false>`, `date_joined=<YYYY-MM-DD>`.

---

## Error Shape (DRF/Djoser)

Typical validation errors:
```json
{
  "detail": "Readable message"
  // or field errors:
  // "email": ["This field is required."],
  // "non_field_errors": ["Some cross-field error"]
}
```

---

## Notes & Implementation Details

- **Auth model:** Custom token serializer allows login by **email or username** while Djoser’s `LOGIN_FIELD` is configured for email.  
- **JWT:** Short access tokens + sliding/rotating refresh with blacklist after rotation.  
- **Media:** Avatars are served from `/media/...`; serializer exposes an absolute `avatar_url`.  
- **CORS:** Enabled via `django-cors-headers` (see `settings.py`).  
- **Pagination:** Standard DRF page format `count/next/previous/results`.
