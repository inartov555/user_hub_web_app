# --- Builder: install deps into a venv (layer-cached by requirements hash)

FROM python:3.12-slim AS builder
ENV VIRTUAL_ENV=/home/pwuser/venv \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install GNU gettext (provides msgfmt) in the runtime
RUN apt-get update \
 && apt-get install -y --no-install-recommends gettext gosu \
 && rm -rf /var/lib/apt/lists/*

RUN addgroup --system pwuser \
 && adduser  --system --ingroup pwuser --disabled-password --home /home/pwuser pwuser

# Now copy the app code (doesn't bust dependency layer unless reqs changed)
COPY backend/ /app/
WORKDIR /app

RUN chown -R pwuser:pwuser /app
USER pwuser

RUN python -m venv "$VIRTUAL_ENV" \
 && chown -R pwuser:pwuser /app /home/pwuser
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --upgrade pip && \
    if [ -f requirements.txt ]; then pip install -r requirements.txt; fi && \
    if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi

# Validate .po syntax (correct paths: /app/locale/**)
RUN sh -c 'set -eu; \
  for PO in $(find /app -type f -path "*/locale/*/LC_MESSAGES/*.po"); do \
    echo "Validating *.po file: $PO"; \
    msgfmt -c -o /dev/null "$PO"; \
  done'

# Compile all message catalogs (manage.py is at /app/manage.py)
# RUN python manage.py compilemessages -v 2

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

RUN mkdir -p /app/media
RUN chown -R pwuser:pwuser /app/media

EXPOSE 8000

CMD python manage.py runserver 0.0.0.0:8000
