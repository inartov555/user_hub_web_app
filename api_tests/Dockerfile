# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS builder

# Python & pip defaults
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /tests

# Install GNU gettext (provides msgfmt) in the runtime
# Cache apt metadata + deb downloads across builds
RUN --mount=type=cache,id=apt-lists,target=/var/lib/apt/lists,sharing=locked \
    --mount=type=cache,id=apt-cache,target=/var/cache/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends gettext gosu

RUN set -eux; \
    if ! getent group pwuser >/dev/null; then addgroup --system pwuser; fi; \
    if ! id -u pwuser >/dev/null 2>&1; then \
      adduser --system --ingroup pwuser --disabled-password --home /home/pwuser pwuser; \
    fi

COPY ./requirements*.txt /tests/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY . /tests

# PW_BROWSER is set in the run_tests.sh file
# Install branded browser channels only when requested (msedge/chrome)
RUN set -eux; \
  if [ "$PW_BROWSER" = "msedge" ] || [ "$PW_BROWSER" = "chrome" ]; then \
    echo "Installing browser channel: $PW_BROWSER"; \
    apt-get update && \
      python -m playwright install --with-deps "$PW_BROWSER" && \
      rm -rf /var/lib/apt/lists/*; \
  fi

# Validate .po syntax (correct paths: /tests/locale/**)
RUN sh -c 'set -eu; \
  for PO in $(find /tests -type f -path "*/locale/*/LC_MESSAGES/*.po"); do \
    echo "Validating *.po file: $PO"; \
    msgfmt -c -o /dev/null "$PO"; \
  done'

# Compile all PO files to MO without importing Django
# This finds every 'django.po' in any tests/locale/<lang>/LC_MESSAGES/
RUN sh -c 'set -eu; \
  for PO in $(find /tests -type f -path "*/locale/*/LC_MESSAGES/*.po"); do \
    MO="${PO%.po}.mo"; \
    echo "Compiling $PO -> $MO"; \
    msgfmt -c -o "$MO" "$PO"; \
  done'

# Confirm compiled catalogs exist
RUN sh -c 'set -eu; \
  for MO in $(find /tests -type f -path "*/locale/*/LC_MESSAGES/*.mo"); do \
    echo "Found compiled catalog: $MO"; \
    ls -l "$MO"; \
  done'

RUN chown -R pwuser:pwuser /tests
USER pwuser

# TEST_GREP is set in the run_tests.sh file
CMD bash -lc "python -m pytest -v --tb=short -s --html='$HOST_ARTIFACTS/test_report_$(date +%Y-%m-%d_%H-%M-%S).html' $TEST_GREP"
