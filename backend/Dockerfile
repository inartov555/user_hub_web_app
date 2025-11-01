# --- builder: install deps into a venv (layer-cached by requirements hash)
FROM python:3.12-slim AS builder
ENV VIRTUAL_ENV=/opt/venv \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Create a compatibility symlink so compilemessages can find the catalogs
# RUN if [ -d /app/locale ] && [ ! -d /app/locale ]; then ln -s /app/locale /app/locale; fi

# now copy the app code (doesn't bust dependency layer unless reqs changed)
COPY backend/ /app/
WORKDIR /app

RUN pip install --upgrade pip && \
    if [ -f requirements.txt ]; then pip install -r requirements.txt; fi && \
    if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi

# Install GNU gettext (provides msgfmt) in the runtime image
RUN apt-get update \
 && apt-get install -y --no-install-recommends gettext \
 && rm -rf /var/lib/apt/lists/*

# OPTIONAL: validate .po syntax (correct paths: /app/locale/**)
RUN msgfmt -c -o /dev/null locale/en_US/LC_MESSAGES/*.po \
 && msgfmt -c -o /dev/null locale/uk_UA/LC_MESSAGES/*.po \
 && msgfmt -c -o /dev/null locale/et_EE/LC_MESSAGES/*.po \
 && msgfmt -c -o /dev/null locale/fi_FI/LC_MESSAGES/*.po \
 && msgfmt -c -o /dev/null locale/cs_CZ/LC_MESSAGES/*.po \
 && msgfmt -c -o /dev/null locale/pl_PL/LC_MESSAGES/*.po \
 && msgfmt -c -o /dev/null locale/es_ES/LC_MESSAGES/*.po

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
RUN ls -l locale/en_US/LC_MESSAGES/*.mo
RUN ls -l locale/uk_UA/LC_MESSAGES/*.mo
RUN ls -l locale/et_EE/LC_MESSAGES/*.mo
RUN ls -l locale/fi_FI/LC_MESSAGES/*.mo
RUN ls -l locale/cs_CZ/LC_MESSAGES/*.mo
RUN ls -l locale/pl_PL/LC_MESSAGES/*.mo
RUN ls -l locale/es_ES/LC_MESSAGES/*.mo

EXPOSE 8000
# don't run pip install at container start!
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# In production you’d do: CMD ["gunicorn", "core.wsgi:application", "-b", "0.0.0.0:8000"]
