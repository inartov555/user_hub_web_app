# API Tests (UsersApp)

A lightweight **API test suite** for the UsersApp backend, built with **pytest** + **requests**.

The tests cover authentication (JWT), user management, profile endpoints, system settings (admin-only), and Excel import/export.

---

## What’s in this repo

- **`tests/`** – pytest test cases
- **`api/`** – a small API client (`UsersAppApi`) used by tests
- **`conftest.py`** – shared fixtures (config, pre-test setup, cleanup helpers)
- **`pytest.ini`** – default target host/port and base API URI
- **`run_tests.sh` + `setup.sh`** – run tests in Docker and store artifacts (logs + HTML report)
- **`docker-compose.yml` + `Dockerfile`** – containerized test runner

---

## Prerequisites

- Docker + Docker Compose

(Optional, if you want to run locally without Docker)
- Python 3.12+

---

## Quick start (Docker)

1. **Make sure the UsersApp is running and reachable** from your machine.
   - By default the tests target: `http://host.docker.internal:5173/api/v1/`
   - If your API is exposed directly on another host/port, update `pytest.ini` (see below).

2. **Run the test suite**:

```bash
chmod +x run_tests.sh setup.sh
./run_tests.sh
```

This will:
- create a workspace under `~/TEST1/workspace/`
- mount an artifacts folder into the container
- build the Docker image and run pytest
- generate an **HTML report** and logs in the artifacts folder

---

## Configuration

### Target host/port

Edit `pytest.ini`:

```ini
[pytest]
base_url = http://host.docker.internal
base_port = 5173
base_api_uri = /api/v1/
```

Examples:
- API directly on port 8000:
  - `base_port = 8000`
- Running against a remote environment:
  - `base_url = https://my-env.example.com`
  - `base_port = 443`

### Using a different ini file

`run_tests.sh` accepts an optional second argument – path to a custom ini file:

```bash
./run_tests.sh false my_env.ini
```

The script copies it into the Docker workspace as `pytest.ini`.

---

## Running a subset of tests

In `run_tests.sh`, edit `TEST_GREP`:

```bash
# Run only matching tests
TEST_GREP="$TEST_GREP -k 'test_get_profile_details'"

# Optional: reruns
# TEST_GREP="$TEST_GREP --reruns 2 --reruns-delay 2"

# Optional: parallel
# TEST_GREP="$TEST_GREP -n auto"
```

---

## Credentials used by tests

Defaults are defined in `conftest.py`:

- Admin: `admin / changeme123`
- Regular user: `test1 / changeme123`

Before the test session starts, the suite tries to **create the regular user** (and ignores the error if it already exists).

---

## Artifacts and reports

Artifacts are stored on the host under:

```
~/TEST1/workspace/artifacts/run-YYYYMMDD-HHMMSS/
```

You should find:
- `pytest/log/...` (log file)
- `test_report_YYYY-MM-DD_HH-MM-SS.html` (pytest-html report)

---

## Local run (without Docker)

If you prefer to run locally:

```bash
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
pytest -v
```

> Note: The repo includes Docker-first scripts. If you uncomment the local-venv lines in `setup.sh`, you can also reuse those scripts.

---

## Troubleshooting

- **`host.docker.internal` not resolving (Linux):**
  This repo already sets `extra_hosts: host.docker.internal:host-gateway` in `docker-compose.yml`.

- **401/403 failures:**
  Confirm the UsersApp is running and the default credentials match your environment.

- **Wrong target environment:**
  Update `pytest.ini` to point at the correct host/port/base path.

---

## License

Add your project license here (MIT/Apache-2.0/etc.).
