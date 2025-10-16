#!/bin/bash

# Input parameters:
#   - $1 - true - delete the DB data after stopping the service;
#          false - preserve the DB data after stopping the service;
#          default = false
#   - $2 - true - starting service with cached data (allows to start the service faster);
#          false - starting the service without cache (cache is cleared)
#          default = false

clean_data_at_exit=${1:-false}
clear_cache=${2:-false}

set -Eeuo pipefail

cleanup_data() {
  echo "Cleaning up..."
  # Shutting down services
  docker compose down -v --remove-orphans
  echo "Done."
  echo "Returning to the original project path to be able to run the test again with new changes, if there are any"
  cd "$ORIGINAL_PROJECT_PATH"
}

cleanup() {
  echo "Returning to the original project path to be able to run the test again with new changes, if there are any"
  cd "$ORIGINAL_PROJECT_PATH"
}

SUPERUSER_EMAIL="${DJANGO_SUPERUSER_EMAIL:-admin@example.com}"
SUPERUSER_PASSWORD="${DJANGO_SUPERUSER_PASSWORD:-changeme123}"

echo "Setting the exit function..."
case "$clean_data_at_exit" in
  true)
    echo "DB will be cleaned up when stopping the service"
    trap cleanup_data EXIT ERR SIGINT SIGTERM
    ;;
  *)
    echo "DB will be preserved when stopping the service"
    trap cleanup EXIT ERR SIGINT SIGTERM
esac

echo "Building images..."
case "$clear_cache" in
  true)
    echo "Cache will be cleared when starting the service"
    docker compose build db
    docker compose build backend
    docker compose build frontend
    ;;
  *)
    echo "Cache will be preserved when starting the service"
    docker compose build db --no-cache
    docker compose build backend --no-cache
    docker compose build frontend --no-cache
esac

ORIGINAL_PROJECT_PATH="$(pwd)"
source ./setup.sh || { echo "setup.sh failed"; exit 1; }
if [[ $? -ne 0 ]]; then
  return 1
fi

echo "Starting Postgres..."
# docker compose up -d db

echo "Making migrations (one-off container)..."
docker compose run --rm backend python manage.py makemigrations profiles

echo "Applying migrations..."
docker compose run --rm backend python manage.py migrate --noinput

# docker compose run --rm \
#  -e DJANGO_SUPERUSER_EMAIL="$SUPERUSER_EMAIL" \
#  -e DJANGO_SUPERUSER_PASSWORD="$SUPERUSER_PASSWORD" \
#  backend python manage.py createsuperuser --noinput

echo "Starting the service"
docker compose up

# cleanup()

# OPTIONAL: fix a bad state where migration was recorded but table missing
# docker compose run --rm backend python manage.py migrate profiles zero --fake
# docker compose run --rm backend python manage.py migrate --noinput

echo "Starting backend & frontend..."
# docker compose up -d backend
# docker compose up -d frontend

# echo "Testing..."
# docker compose exec backend python manage.py test --noinput -v 2

# echo "Collecting statistics..."
# docker compose exec backend python manage.py collectstatic --noinput

# echo "Creating superuser..."
# docker compose exec backend python manage.py createsuperuser --noinput
