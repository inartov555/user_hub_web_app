# Users App UI Automation (Pytest + Playwright + Django + Docker)

- This folder contains a **UI automation framework** for the attached Users App (`users_app` folder in the root project directory).
- Created on Nov-05-2025

## Stack

- **Python** + **Pytest**
- **Playwright** (Chromium, Firefox, WebKit)
- **Django backend** (the existing app) – used as the system under test, including its i18n and logging setup
- **Docker / docker-compose** – one stack for Django + Postgres + frontend + Playwright tests
- **Page Object Model (POM)** – one page-object class per UI page

All Python modules, classes and functions include docstrings and return-type hints.

## Prerequisites

- Start the Users App web site (`users_app` folder in the root project directory)
- Create 2 users before running tests:
```
     a) Regular user: test1 / changeme123
     b) Admin: admin / changeme123
```
- Docker & docker-compose installed
- Python is only required inside the Docker image; host Python is optional

## How to run

1. Start tests

   ```
   #     Clearing cache before starting service
   #   - $1 - true - starting service WITHOUT cached data (allows to start the service faster);
   #          false - starting the service WITH cache (cache is cleared)
   #          default = false
   #
   #     pytest.ini config file
   #   - $2 - the path to the *.ini config file, defaults to pytest.ini

   # (1) Defaults to (2)
   ./run_tests.sh

   # (2) Run tests using Docker compose (reusing build cache)
   ./run_tests.sh false pytest.ini

   # (3) Run tests with a clean image build (no cache)
   ./run_tests.sh true pytest.ini
   ```

2. Copied project folder, run results like logs, etc., are located in: `/home/$user_name/TEST1/workspace`. Artifacts (run results, logs, etc.) are located in: `/home/$user_name/TEST1/workspace/artifacts`.

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

