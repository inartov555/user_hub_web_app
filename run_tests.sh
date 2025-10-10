#!/bin/bash

# Input parameters:
#   - NONE

ORIGINAL_PROJECT_PATH="$(pwd)"
eval source ./setup.sh
if [[ $? -ne 0 ]]; then
  return 1
fi

docker compose up --build -d
docker compose exec backend python manage.py createsuperuser

# Returning to the original project path to be able to run the test again with new changes, if there are any
cd "$ORIGINAL_PROJECT_PATH"
