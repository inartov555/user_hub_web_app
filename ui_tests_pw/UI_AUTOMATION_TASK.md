
# QA UI Automation Task – Users App

This change adds a **Python + Pytest + Playwright** UI automation test suite (POM architecture) that
covers *all pages* of the Users App, including:

- Authentication (login, protected routes) with **negative cases**
- Admin flows: **Settings**, **Stats**, **Excel Import**
- User flows: **Users table**, **Profile view/edit**, **Change password**
- **Localization** checks across multiple locales
- **Light/Dark mode** toggle behavior
- **Session expiration** and **refresh token rotation** (proactive refresh via Axios interceptor)

It also adds a **Dockerized** test runner and a `docker-compose` override to run tests **in parallel** across **Chromium, Firefox, and WebKit**.

## How to run

1. Start the stack:

```bash
docker compose up -d --build
```

2. Run the UI tests:

```bash
docker compose -f docker-compose.yml -f docker-compose.ui-tests.yml up --build --abort-on-container-exit --exit-code-from uitests
```

### Local (without Docker)

```bash
cd ui_tests
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install
pytest -vv --base-url=http://localhost:5173 --browser=all -n auto
```

## Notes on implementation

- **POM**: Page objects live under `ui_tests/pages`. They encapsulate navigations and stable selectors.
- **Parallelization**: Enabled via `pytest-xdist` (`--numprocesses=auto`) and Playwright’s multi-browser execution.
- **Browsers**: Chromium, Firefox, WebKit (via `--browser ...`). Default is all in `pytest.ini`.
- **i18n**: Tests set `localStorage.i18nextLng` to a target locale and reload.
- **Theme**: Toggled via the `#lightDarkMode` control; assertions inspect the `<html>` classList (`dark`).
- **Auth expiry & rotation**: Admin test helper reduces token lifetimes (via `/system/settings/`) and then
  observes `localStorage.refresh` rotating and redirect to `/login` after expiry.
- **Negative cases**: Bad login, protected route redirects, wrong old password, and admin‑only pages.

Credentials used:

- Regular user: `test1 / megaboss19`
- Admin: `admin / changeme123`
- Frontend URL: `http://localhost:5173/`

