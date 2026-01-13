## 💡 Users App UI Automation (Pytest + Playwright + Django + Docker)

- This folder contains a UI automation framework for the attached Users App (`users_app` folder in the root project directory).
- Created on Nov-05-2025

---

[List of automation tests](./LIST_OF_TESTS.md)

---

## 🧰 Stack

- **Python** + **Pytest**
- **Playwright** (Chromium, Chrome, MS Edge, Firefox, WebKit, Safari)
- **Django backend** (the existing app) – used as the system under test, including its i18n setup
- **Docker / docker-compose** – one stack for Django (for localization tests) + Playwright tests
- **Page Object Model (POM)** – one page-object class per UI page

## 🔑 Prerequisites

- **The test launch was tested against the Linux Ubuntu OS**
- Start the Users App website (`users_app` folder in the root project directory)
- Docker & docker-compose installed
- Python is only required inside the Docker image

## 🚀 How to run

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

## 🗂️ High-level test strategy

- UI-centric tests that exercise the real Django REST backend and React SPA.
- One POM per logical page:
  - Login,
  - Signup,
  - Reset Password
  - About
  - Users Table
  - Profile View
  - Profile Edit
  - Settings
  - User Stats
  - Excel Import
  - Change Password
  - User Delete Confirm
- For each page, at least one scenario is covered when the suite is executed:
  - Dark/light theme behavior
  - Localization (English + at least one non-English locale)
  - Access control for:
    - Admin: `admin / changeme123` (created automatically after first website start)
    - Regular user: `test1 / changeme123` (created automatically by the automation framework before starting the tests)
- The Users table page gets additional coverage for:
  - Multi-column sorting state & indicators
  - Admin-only controls (`Delete users`, `Change password` column)
  - Non-admin restrictions

## ✨ Where Django is used in tests

- Helper utilities in `tests/utils/django_localization.py` can initialize Django and read its language configuration for cross-checks (e.g., ensuring UI locale options match server locales).

