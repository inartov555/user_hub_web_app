# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS builder

# Python & pip defaults
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_CACHE_DIR=/root/.cache/pip

WORKDIR /app

# Install GNU gettext (provides msgfmt) in the runtime
# Cache apt metadata + deb downloads across builds
RUN --mount=type=cache,id=apt-lists,target=/var/lib/apt/lists,sharing=locked \
    --mount=type=cache,id=apt-cache,target=/var/cache/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends gettext gosu

RUN addgroup --system pwuser \
 && adduser  --system --ingroup pwuser --disabled-password --home /home/pwuser pwuser

# RUN pip install --upgrade pip && \
#    if [ -f requirements.txt ]; then pip install -r requirements.txt; fi && \
#    if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi

COPY backend/requirements*.txt /app/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY backend/ /app/

# Validate .po syntax (correct paths: /app/locale/**)
RUN sh -c 'set -eu; \
  for PO in $(find /app -type f -path "*/locale/*/LC_MESSAGES/*.po"); do \
    echo "Validating *.po file: $PO"; \
    msgfmt -c -o /dev/null "$PO"; \
  done'

# Compile all PO files to MO without importing Django
# This finds every 'django.po' in any app/locale/<lang>/LC_MESSAGES/
RUN sh -c 'set -eu; \
  for PO in $(find /app -type f -path "*/locale/*/LC_MESSAGES/*.po"); do \
    MO="${PO%.po}.mo"; \
    echo "Compiling $PO -> $MO"; \
    msgfmt -c -o "$MO" "$PO"; \
  done'

# Confirm compiled catalogs exist
RUN sh -c 'set -eu; \
  for MO in $(find /app -type f -path "*/locale/*/LC_MESSAGES/*.mo"); do \
    echo "Found compiled catalog: $MO"; \
    ls -l "$MO"; \
  done'

RUN chown -R pwuser:pwuser /app
RUN mkdir -p /app/media
RUN chown -R pwuser:pwuser /app/media
USER pwuser

EXPOSE 8000

CMD python manage.py runserver 0.0.0.0:8000
