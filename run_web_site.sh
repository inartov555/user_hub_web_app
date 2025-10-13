#!/bin/bash

# Input parameters:
#   - NONE

set -Eeuo pipefail

SUPERUSER_EMAIL="${DJANGO_SUPERUSER_EMAIL:-admin@example.com}"
SUPERUSER_PASSWORD="${DJANGO_SUPERUSER_PASSWORD:-changeme123}"

cleanup() {
  echo "Cleaning up..."
  # Shutting down services
  docker compose down -v --remove-orphans
  echo "Done."
  echo "Returning to the original project path to be able to run the test again with new changes, if there are any"
  cd "$ORIGINAL_PROJECT_PATH"
}
trap cleanup SIGINT SIGTERM

ORIGINAL_PROJECT_PATH="$(pwd)"
eval source ./setup.sh
if [[ $? -ne 0 ]]; then
  return 1
fi

echo "Building images..."
docker compose build db --no-cache
docker compose build backend --no-cache
docker compose build frontend --no-cache

echo "Starting Postgres..."
# docker compose up -d db

echo "Making migrations (one-off container)..."
docker compose run --rm backend python manage.py makemigrations profiles

echo "Applying migrations..."
docker compose run --rm backend python manage.py migrate --noinput
docker compose run --rm \
  -e DJANGO_SUPERUSER_EMAIL="$SUPERUSER_EMAIL" \
  -e DJANGO_SUPERUSER_PASSWORD="$SUPERUSER_PASSWORD" \
  backend python manage.py createsuperuser --noinput

# OPTIONAL: fix a bad state where migration was recorded but table missing
# docker compose run --rm backend python manage.py migrate profiles zero --fake
# docker compose run --rm backend python manage.py migrate --noinput

echo "Starting backend & frontend..."
# docker compose up -d backend
# docker compose up -d frontend

docker compose up

cleanup()

# echo "Testing..."
# docker compose exec backend python manage.py test --noinput -v 2

# echo "Collecting statistics..."
# docker compose exec backend python manage.py collectstatic --noinput

# echo "Creating superuser..."
# docker compose exec backend python manage.py createsuperuser --noinput
