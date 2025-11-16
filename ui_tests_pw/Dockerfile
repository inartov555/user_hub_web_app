"""Dockerfile for Playwright-based UI tests."""
FROM mcr.microsoft.com/playwright/python:v1.55.0-noble

WORKDIR /app

# Copy backend requirements first (Django + DRF) and install them.
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy UI test requirements and install them.
COPY ui_tests/requirements.txt ui_tests/requirements.txt
RUN pip install --no-cache-dir -r ui_tests/requirements.txt

# Install Playwright browsers explicitly (the base image contains browser deps).
RUN python -m playwright install --with-deps

# Copy the full repository (backend, frontend, ui_tests, etc.).
COPY . .

ENV UI_BASE_URL=http://frontend
ENV UI_BASE_PORT=80
ENV BACKEND_API_BASE=http://backend:8000/api/v1
ENV DJANGO_SETTINGS_MODULE=core.settings
ENV PYTHONUNBUFFERED=1

# Wait for the frontend to be up, then run pytest.
CMD ["bash", "ui_tests/run_ui_tests.sh"]
