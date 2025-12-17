FROM mcr.microsoft.com/playwright/python:v1.57.0-jammy

# RUN addgroup --system pwuser \
# && adduser  --system --ingroup pwuser --disabled-password --home /home/pwuser pwuser

# Saner Python & pip defaults
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /tests
COPY . /tests

# RUN apt-get update && apt-get install -y --no-install-recommends xvfb \
#  && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python-is-python3 \
    && rm -rf /var/lib/apt/lists/*

RUN chown -R pwuser:pwuser /tests
USER pwuser

RUN --mount=type=cache,target=.cache/pip \
    python -m pip install -U pip && \
    pip install -r requirements.txt

# Default behavior: run the tests suite (with a virtual display)
# CMD bash -lc "xvfb-run -a -s '-screen 0 1920x1080x24' python -m pytest -v --tb=short -s --html='$HOST_ARTIFACTS/test_report_$(date +%Y-%m-%d_%H-%M-%S).html' $TEST_GREP"
CMD bash -lc "python -m pytest -v --tb=short -s --html='$HOST_ARTIFACTS/test_report_$(date +%Y-%m-%d_%H-%M-%S).html' $TEST_GREP"
