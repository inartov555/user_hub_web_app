# --- builder: install deps into a venv (layer-cached by requirements hash)
FROM python:3.12-slim AS builder
ENV VIRTUAL_ENV=/opt/venv \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app
# copy only requirements files first to leverage Docker layer cache
COPY backend/requirements*.txt /app/
RUN pip install --upgrade pip && \
    if [ -f requirements.txt ]; then pip install -r requirements.txt; fi && \
    if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi

# --- runtime
FROM python:3.12-slim AS runtime
ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# copy prebuilt venv from builder
COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
# now copy the app code (doesn't bust dependency layer unless reqs changed)
COPY backend/ /app/

EXPOSE 8000
# don't run pip install at container start!
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# In production you’d do: CMD ["gunicorn", "core.wsgi:application", "-b", "0.0.0.0:8000"]
