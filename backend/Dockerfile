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

WORKDIR /app
# now copy the app code (doesn't bust dependency layer unless reqs changed)
COPY backend/ /app/

RUN pip install --upgrade pip && \
    if [ -f requirements.txt ]; then pip install -r requirements.txt; fi && \
    if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi

# Install GNU gettext (provides msgfmt) in the runtime image
RUN apt-get update \
 && apt-get install -y --no-install-recommends gettext \
 && rm -rf /var/lib/apt/lists/*

# Compile translations after code is copied & deps installed
# If your manage.py is one level up, adjust WORKDIR accordingly
# RUN python -m django compilemessages -l et -l en -v 2
# RUN django-admin compilemessages -l et_EE -l en_US -v 2
RUN python manage.py compilemessages -v 2

EXPOSE 8000
# don't run pip install at container start!
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# In production you’d do: CMD ["gunicorn", "core.wsgi:application", "-b", "0.0.0.0:8000"]
