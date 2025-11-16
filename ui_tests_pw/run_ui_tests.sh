#!/usr/bin/env bash
"""Entrypoint script for the Playwright UI tests container."""
set -euo pipefail

echo "[ui-tests] Waiting for frontend to become available..."

python - << 'PYCODE'
import os
import socket
import time

host = os.environ.get("UI_BASE_URL", "http://frontend").replace("http://", "").replace("https://", "")
port = int(os.environ.get("UI_BASE_PORT", "80"))

def wait_for_port(host: str, port: int, timeout: float = 180.0) -> None:
    """Wait until a TCP port is open, or raise TimeoutError."""
    deadline = time.time() + timeout
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=5.0):
                print(f"[ui-tests] {host}:{port} is up.")
                return
        except OSError as exc:
            last_err = exc
            print(f"[ui-tests] Waiting for {host}:{port} ... {exc}")
            time.sleep(2.0)
    raise TimeoutError(f"Timed out waiting for {host}:{port}") from last_err

wait_for_port(host, port)
PYCODE

echo "[ui-tests] Starting pytest with Playwright..."
pytest -c ui_tests/pytest.ini -n auto --browser chromium --browser firefox --browser webkit ui_tests/tests
