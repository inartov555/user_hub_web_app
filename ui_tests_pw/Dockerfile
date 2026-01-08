FROM mcr.microsoft.com/playwright/python:v1.57.0-jammy

ARG PW_BROWSER=chromium
ENV PW_BROWSER=${PW_BROWSER}

# Python & pip defaults
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /tests
COPY . /tests

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python-is-python3 \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update \
 && apt-get install -y --no-install-recommends gettext gosu \
 && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=.cache/pip \
    python -m pip install -U pip && \
    pip install -r requirements.txt

# PW_BROWSER is set in the run_test.sh file
# Install branded browser channels only when requested (msedge/chrome)
RUN set -eux; \
  if [ "$PW_BROWSER" = "msedge" ] || [ "$PW_BROWSER" = "chrome" ]; then \
    echo "Installing browser channel: $PW_BROWSER"; \
    apt-get update && \
      python -m playwright install --with-deps "$PW_BROWSER" && \
      rm -rf /var/lib/apt/lists/*; \
  fi

RUN chown -R pwuser:pwuser /tests
USER pwuser

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

# TEST_GREP is set in the run_test.sh file
CMD bash -lc "python -m pytest -v --tb=short -s --html='$HOST_ARTIFACTS/test_report_$(date +%Y-%m-%d_%H-%M-%S).html' $TEST_GREP"
