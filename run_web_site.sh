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

echo "Building images..."
docker compose build --no-cache

echo "Starting services..."
docker compose up --build

echo "Applying migrations..."
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate --noinput

echo "Creating superuser..."
docker compose exec backend python manage.py createsuperuser

# Returning to the original project path to be able to run the test again with new changes, if there are any
cd "$ORIGINAL_PROJECT_PATH"
