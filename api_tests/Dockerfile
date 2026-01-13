# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS builder

# Python & pip defaults
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /tests

RUN set -eux; \
    if ! getent group pwuser >/dev/null; then addgroup --system pwuser; fi; \
    if ! id -u pwuser >/dev/null 2>&1; then \
      adduser --system --ingroup pwuser --disabled-password --home /home/pwuser pwuser; \
    fi

COPY ./requirements*.txt /tests/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY . /tests

RUN chown -R pwuser:pwuser /tests
USER pwuser

# TEST_GREP is set in the run_tests.sh file
CMD bash -lc "python -m pytest -v --tb=short -s --html='$HOST_ARTIFACTS/test_report_$(date +%Y-%m-%d_%H-%M-%S).html' $TEST_GREP"
