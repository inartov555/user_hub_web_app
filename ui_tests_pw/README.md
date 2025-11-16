# Users App UI Automation (Pytest + Playwright + Django + Docker)

This folder contains a **UI automation framework** for the attached Users App.

## Stack

- **Python** + **Pytest**
- **Playwright** (Chromium, Firefox, WebKit)
- **Django backend** (the existing app) – used as the system under test, including its i18n and logging setup
- **Docker / docker-compose** – one stack for Django + Postgres + frontend + Playwright tests
- **Page Object Model (POM)** – one page-object class per UI page

All Python modules, classes and functions include docstrings and return-type hints.

## Prerequisites

From the `users_app` project root (this directory lives inside that repo):

- Docker & docker-compose installed
- Python is only required inside the Docker image; host Python is optional

## How to run

1. Build and start the stack **including tests**:

   ```bash
   docker compose -f docker-compose.yml -f ui_tests/docker-compose.ui-tests.yml up --build --abort-on-container-exit
   ```

   This starts:
   - Postgres
   - Django backend (with logging & i18n)
   - React frontend (served via nginx)
   - A one-shot **Playwright test container** that waits for the app to be ready and then runs `pytest`.

2. To re-run tests only, after the stack is built:

   ```bash
   docker compose -f docker-compose.yml -f ui_tests/docker-compose.ui-tests.yml run --rm ui-tests
   ```

3. To run tests locally without Docker (e.g., for IDE debugging):

   ```bash
   cd ui_tests
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   playwright install --with-deps

   # Make sure the app is already running at http://localhost:5173
   pytest --browser chromium
   ```

## Parallel & multi-browser execution

- Parallel tests (via `pytest-xdist`):

  ```bash
  pytest -n auto
  ```

- Run on **all Playwright browsers**:

  ```bash
  pytest --browser chromium --browser firefox --browser webkit
  ```

Playwright’s pytest plugin wires these arguments to the built-in `browser`, `context` and `page` fixtures.

## High-level test strategy

- UI-centric tests that exercise the real **Django REST backend** and **React SPA**.
- One POM per logical page:
  - Login, Signup, Reset password
  - Users table
  - Profile view / edit
  - Settings
  - Stats
  - Excel import
  - Change password
  - User delete confirm
- For **each page** we cover at least ten scenarios when the suite is executed:
  - Dark/light theme behavior
  - Localization (English + at least one non-English locale)
  - Access control for:
    - Regular user: `test1 / changeme123`
    - Admin: `admin / changeme123`
- The **Users table** page gets additional coverage for:
  - Multi-column sorting state & indicators
  - Admin-only controls (`Delete users`, `Change password` column)
  - Non-admin restrictions

## Where Django is used from tests

- The backend runs as part of the Docker stack and provides:
  - Configured localization (`LocaleMiddleware`, compiled translations)
  - Structured logging (console + rotating log files, as configured in `core.settings.LOGGING`)
- Optionally, helper utilities in `tests/utils/django_localization.py` can initialize Django and
  read its language configuration for cross-checks (e.g., ensuring UI locale options match server locales).

