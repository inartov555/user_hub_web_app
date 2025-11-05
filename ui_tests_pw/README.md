
# UI Tests (Playwright + Pytest) for Users App

This folder contains a **Python + Playwright** end‑to‑end test suite that exercises the Users App (Django backend, React SPA).  
It is designed for **parallel** execution across **all supported browsers** and runs cleanly in **Docker**.

## Highlights

- ✅ Pytest + Playwright (Python) with **Page Object Model** (`ui_tests/pages`)
- ✅ **Parallel** test execution via `pytest-xdist`
- ✅ Runs on **Chromium, Firefox, WebKit** in one command
- ✅ Covers **authentication** (login, protected routes), **negative cases**
- ✅ Exercises **refresh token rotation** and **session expiration**
- ✅ **Localization (i18n)** assertions across multiple locales
- ✅ **Light/Dark theme** toggle checks
- ✅ Admin flows: **Settings**, **Excel import**, **Stats**
- ✅ Dockerized test runner with a `docker-compose` override

## Quick start (Docker)

Assuming the app is running with:

```bash
docker compose up -d --build
# or: ./run_web_site.sh
```

Run the UI tests in a dedicated container:

```bash
docker compose -f docker-compose.yml -f docker-compose.ui-tests.yml up --build --abort-on-container-exit --exit-code-from uitests
```

The test runner waits until the frontend is reachable, then executes:

- All tests in parallel (`-n auto`)
- All browsers (`--browser chromium --browser firefox --browser webkit`)

## Local run (no Docker)

```bash
cd ui_tests
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install
pytest -vv --base-url=http://localhost:5173 --browser=all -n auto
```

## Test data & credentials

- Regular user: `test1 / megaboss19`  
- Admin user: `admin / changeme123`  
- Default base URL: `http://localhost:5173/` (configurable via `BASE_URL`)

Excel import uses the template at `test_data/import_template_EXAMPLE.xlsx`.

## Structure

```
ui_tests/
  pages/
    base_page.py
    login_page.py
    users_page.py
    profile_pages.py
    settings_page.py
    excel_import_page.py
    stats_page.py
  tests/
    test_auth_login.py
    test_localization.py
    test_theme.py
    test_users_pages.py
    test_admin_pages.py
    test_refresh_rotation.py
  pytest.ini
  pyproject.toml
  requirements.txt
  Dockerfile
  wait-for-http.sh
```

## Notes

- **Auth & expiry tests**: The suite updates server auth settings to short TTLs (via admin API) to reliably test
  proactive refresh and redirect on expiry.
- **Localization**: Uses `i18next`’s `localStorage` key (`i18nextLng`) to switch languages, then asserts translated UI.
- **Selectors**: Prefer **semantic locators** (`get_by_role`, `get_by_label`) for resilience. Only fall back to IDs when present.
- **Parallel safety**: Each test clears `localStorage`/`sessionStorage` to avoid cross‑pollution; API calls are stateless.

## Environment variables

| Var | Purpose | Default |
|-----|---------|---------|
| `BASE_URL` | Frontend URL used by Playwright | `http://localhost:5173` |
| `API_URL` | Backend API base (for token/settings helpers) | `http://localhost:8000/api/v1` |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | Admin credentials | `admin` / `changeme123` |
| `USER_USERNAME` / `USER_PASSWORD` | Regular user credentials | `test1` / `megaboss19` |

