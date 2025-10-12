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

# Refreshing Docker groups in the currect shell
# echo ""
# echo "Debug info before starting docker"
# echo ""
# newgrp docker

# For debug reasons
# echo "DOCKER_HOST = '$DOCKER_HOST'"
# echo "$(docker context ls)"
# echo "$(docker version)"
# echo ""
# echo "End of debug info"
# echo ""

docker compose build --no-cache
docker compose up --build

docker compose exec backend python manage.py migrate --database default
docker compose exec backend python manage.py makemigrations profiles
docker compose exec backend python manage.py createsuperuser

# Returning to the original project path to be able to run the test again with new changes, if there are any
cd "$ORIGINAL_PROJECT_PATH"
