#!/bin/bash

# Input parameters:
#   - $1 - true - starting service WITHOUT cached data (allows to start the service faster);
#          false - starting the service WITH cache (cache is cleared)
#          default = false

INI_CONFIG_FILE="${1:-pytest.ini}"
clear_cache=${2:-false}

set -Eeuo pipefail
trap cleanup EXIT ERR SIGINT SIGTERM

cleanup() {
  if [ -n "${VIRTUAL_ENV-}" ] && [ "$(type -t deactivate 2>/dev/null)" = "function" ]; then
    echo "Deactivating venv..."
    deactivate
  fi
  if ! [[ "$ORIGINAL_PROJECT_PATH" -ef "$(pwd)" ]]; then
    echo "Returning to the original project path to be able to run the test again with new changes, if there are any"
    cd "$ORIGINAL_PROJECT_PATH"
  fi
}

ORIGINAL_PROJECT_PATH="$(pwd)"
source ./setup.sh || { echo "setup.sh failed"; exit 1; }
if [[ $? -ne 0 ]]; then
  exit 1
fi

echo "Building images..."
case "$clear_cache" in
  true)
    echo "Cache will be cleared when starting the service"
    # docker compose build tests --no-cache
    ;;
  *)
    echo "Cache will be preserved when starting the service"
    # docker compose build tests
esac

# echo "Starting the tests..."
# docker compose run --rm tests

if [[ ! -f "$INI_CONFIG_FILE" ]]; then
  echo "ERROR: Provided path '$INI_CONFIG_FILE' for the repo does not exist"
  exit 1
else
  echo "Using $INI_CONFIG_FILE ini config file"
fi

# python3 -m pytest -v --tb=short -s --reruns 2 --reruns-delay 2 --ini-config "$INI_CONFIG_FILE" --html=$HOST_ARTIFACTS/test_report_$(date +%Y-%m-%d_%H-%M-%S).html
python3 -m pytest -v --tb=short -k test_admin_can_open_change_password_for_user -s -c "$INI_CONFIG_FILE" --html=$HOST_ARTIFACTS/test_report_$(date +%Y-%m-%d_%H-%M-%S).html

#
#
#
