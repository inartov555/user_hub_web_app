# 💡 API Tests (UsersApp)

A lightweight **API test suite** for the UsersApp backend, built with **pytest** + **requests**.

The tests cover authentication (JWT), user management, profile endpoints, system settings (admin-only), and Excel import/export.

---

## 🔑 Prerequisites

- **The test launch was tested against the Linux Ubuntu OS**
- Start the Users App website (`users_app` folder in the root project directory)
- Docker & docker-compose installed
- Python is only required inside the Docker image

---

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

---

## What’s in this repo

- **`tests/`** – pytest test cases
- **`api/`** – a small API client (`UsersAppApi`) used by tests
- **`conftest.py`** – shared fixtures (config, pre-test setup, cleanup helpers)
- **`pytest.ini`** – default target host/port and base API URI
- **`run_tests.sh` + `setup.sh`** – run tests in Docker and store artifacts (logs + HTML report)
- **`docker-compose.yml` + `Dockerfile`** – containerized test runner

---

## Credentials used by tests

Defaults are defined in `conftest.py`:

- Admin: `admin / changeme123` (created automatically after first website start)
- Regular user: `test1 / changeme123` (created automatically by the automation framework before starting the tests)
