# API Reference

> **Base URL**
>
> All paths below are **relative to** `/api`. When running locally without a reverse proxy, that is typically `http://localhost:8000/api`.
> The frontend Axios client defaults to `baseURL = import.meta.env.VITE_API_URL || "/api"`.

---

## Auth (Djoser + JWT)

### Obtain tokens
**POST** `/auth/jwt/create/`

Request (email or username accepted):
```json
{
  "email": "admin@example.com",   // or use "username": "admin"
  "password": "••••••••"
}
```

Response:
```json
{
  "access": "<JWT_ACCESS>",
  "refresh": "<JWT_REFRESH>"
}
```

### Refresh access token
**POST** `/auth/jwt/refresh/`

Request:
```json
{
  "refresh": "<JWT_REFRESH>"
}
```

Response:
```json
{
  "access": "<NEW_JWT_ACCESS>"
}
```

> Notes:
> - Login field is configured for **email**; a custom serializer also allows **username**.
> - Access token lifetime and refresh timing are tunable; see **System Settings** below.

---

## Users

### List users
**GET** `/users/`

Query params (all optional):
- `page`: integer (pagination)
- `page_size`: integer
- `ordering`: e.g. `username`, `-date_joined`
- `search`: full‑text search across username/email

Response (paginated DRF format):
```json
{
  "count": 123,
  "next": "http://.../users/?page=3",
  "previous": null,
  "results": [
    {
      "id": 7,
      "username": "alice",
      "email": "alice@example.com",
      "is_active": true,
      "is_staff": false,
      "date_joined": "2025-10-15T10:13:20Z"
    }
  ]
}
```

### Retrieve a user
**GET** `/users/{id}/`

Response:
```json
{
  "id": 7,
  "username": "alice",
  "email": "alice@example.com",
  "is_active": true,
  "is_staff": false,
  "date_joined": "2025-10-15T10:13:20Z",
  "profile": {
    "first_name": "Alice",
    "last_name": "Doe",
    "avatar_url": "https://.../media/avatars/alice.jpg"
  }
}
```

### Admin: set a user's password
**POST** `/users/{id}/set_password/`

Request:
```json
{ "password": "NewStrongPassword123!" }
```

Response 200:
```json
{ "detail": "Password updated." }
```

Errors:
- 400 with `{ "detail": "<validation error from password validators>" }`

> Permissions:
> - Listing/retrieving users typically requires staff/admin.
> - Setting another user's password requires admin; self‑service password change is separate (see **Me / Change password**).

---

## Me (current user)

### Get my profile
**GET** `/me/profile/`

Response:
```json
{
  "id": 7,
  "username": "alice",
  "email": "alice@example.com",
  "profile": {
    "first_name": "Alice",
    "last_name": "Doe",
    "bio": "…",
    "avatar_url": "https://..."
  }
}
```

### Update my profile
**PUT** `/me/profile/` *(or PATCH)*

Request:
```json
{
  "profile": {
    "first_name": "Alice",
    "last_name": "Doe",
    "bio": "Updated bio"
  }
}
```

Response mirrors the **Get my profile** payload.

### Change my password
**POST** `/me/profile/change_password/`

Request:
```json
{ "password": "NewStrongPassword123!" }
```

Response 200:
```json
{ "detail": "Password updated." }
```

---

## Excel import

**POST** `/import-excel/` *(multipart form-data)*

- Field name: `file`
- Accepts `.xlsx` in the format of `test_data/import_template_EXAMPLE.xlsx`

Response 200:
```json
{
  "created": 10,
  "updated": 2,
  "skipped": 1,
  "errors": [
    {"row": 7, "message": "Email already exists"}
  ]
}
```

Errors:
- 400 `{ "detail": "Invalid file" }` or row‑level errors in the `errors` array.

---

## Stats

### Online users (last 5 minutes)
**GET** `/stats/online-users/`

Response:
```json
[
  {"id": 7, "username": "alice", "email": "alice@example.com"},
  {"id": 2, "username": "bob",   "email": "bob@example.com"}
]
```

---

## System settings (runtime‑tunable auth)

### Read effective auth settings
**GET** `/system/settings/`

Response:
```json
{
  "ACCESS_TOKEN_LIFETIME": 1800,   // seconds
  "JWT_RENEW_AT_SECONDS": 1200,
  "IDLE_TIMEOUT_SECONDS": 900
}
```

### Update auth settings
**PUT** `/system/settings/`

Request:
```json
{
  "ACCESS_TOKEN_LIFETIME": 1800,
  "JWT_RENEW_AT_SECONDS": 1200,
  "IDLE_TIMEOUT_SECONDS": 900
}
```

Response mirrors **GET**.

Validation:
- All fields are required; integers; with minimums (`IDLE_TIMEOUT_SECONDS` >= 1, etc.).

### Effective runtime (derived) values
**GET** `/system/runtime-auth/`

Response (read‑only; derived from DB + defaults):
```json
{
  "ACCESS_TOKEN_LIFETIME": 1800,
  "JWT_RENEW_AT_SECONDS": 1200,
  "IDLE_TIMEOUT_SECONDS": 900
}
```

---

## Errors & conventions

- All endpoints return standard DRF error formats:
```json
{ "detail": "Error message" }
# or for field errors
{ "field": ["Message 1", "Message 2"] }
```

- Pagination is DRF's page number style (`count`, `next`, `previous`, `results`).
- Auth required unless explicitly public; send `Authorization: Bearer <access>`.
- Media (e.g., avatars) are served from `/media/...` with absolute URLs in serializers.
