#!/bin/bash

# Input parameters:
#   - NONE

ORIGINAL_PROJECT_PATH="$(pwd)"
eval source ./setup.sh
if [[ $? -ne 0 ]]; then
  return 1
fi

cp backend/.env.example backend/.env

docker compose build frontend --no-cache
docker compose build backend --no-cache
docker compose up frontend
docker compose up backend

docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser

# Returning to the original project path to be able to run the test again with new changes, if there are any
cd "$ORIGINAL_PROJECT_PATH"
wait
