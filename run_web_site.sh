#!/bin/bash

# Input parameters:
#   - NONE

# set -euo pipefail
# When this terminal/tab closes (or you press Ctrl-C), stop everything we started.
# trap 'echo "Shutting down…"; kill 0' EXIT INT TERM
# pids=()
# grace=8

cleanup() {
  echo "Stopping services…"
  # Try graceful stop
  kill "${pids[@]}" 2>/dev/null || true
  # Wait up to $grace seconds, then SIGKILL leftovers
  for _ in $(seq "$grace"); do sleep 1; pkill -0 -P $$ || break; done
  kill -9 "${pids[@]}" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

ORIGINAL_PROJECT_PATH="$(pwd)"
eval source ./setup.sh
if [[ $? -ne 0 ]]; then
  return 1
fi

# cd frontend
# npm i
# echo 'VITE_API_URL=http://localhost:8000/api' > .env.local
# npm run dev & pids+=($!)

cp backend/.env.example backend/.env
docker compose build --no-cache
docker compose up
# docker compose exec backend python manage.py createsuperuser & pids+=($!)
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser

# Returning to the original project path to be able to run the test again with new changes, if there are any
cd "$ORIGINAL_PROJECT_PATH"
wait
