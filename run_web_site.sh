#!/bin/bash

# Input parameters:
#   - NONE

set -Eeuo pipefail

cleanup() {
  echo -e "\nCleaning up..."
  # Stop log stream, if alive
  # [[ "${LOGS_PID:-}" ]] && kill "${LOGS_PID}" 2>/dev/null || true
  # Shutting down services
  docker compose down -v --remove-orphans
  sudo systemctl start docker
  echo "Done."
}
trap cleanup SIGINT SIGTERM

ORIGINAL_PROJECT_PATH="$(pwd)"
eval source ./setup.sh
if [[ $? -ne 0 ]]; then
  return 1
fi

cp backend/.env.example backend/.env

echo "Building images..."
docker compose build --no-cache

echo "Starting services..."
docker compose up --build

# Wait for DB to be ready (Postgres example; adjust service name/command if needed)
# echo "Waiting for database..."
# if docker compose ps db >/dev/null 2>&1; then
  # shellcheck disable=SC2016
#  until docker compose exec -T db pg_isready -U "${POSTGRES_USER:-postgres}" >/dev/null 2>&1; do
#    sleep 1
#    printf '.'
#  done
#  echo
# else
  # Fallback: give containers a moment if no dedicated db service
#  sleep 5
# fi

echo "Applying migrations..."
docker compose exec -T backend python manage.py migrate --noinput

docker compose exec backend python manage.py createsuperuser

# Returning to the original project path to be able to run the test again with new changes, if there are any
cd "$ORIGINAL_PROJECT_PATH"
