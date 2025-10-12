#!/bin/bash

# Input parameters:
#   - NONE

set -Eeuo pipefail

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
docker compose build --no-cache

echo "Starting services..."
docker compose up --build

echo "Applying migrations..."
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py makemigrations profiles
docker compose exec backend python manage.py migrate --noinput
echo "Testing..."
docker compose exec backend python manage.py test --noinput -v 2

echo "Collecting statistics..."
docker compose exec backend python manage.py collectstatic --noinput

echo "Creating superuser..."
docker compose exec backend python manage.py createsuperuser
