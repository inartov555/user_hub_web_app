#!/bin/bash

# Input parameters:
#
#     Clearing cache before starting service
#   - $1 - true - starting service WITHOUT cached data (allows to start the service faster);
#          false - starting the service WITH cache (cache is cleared)
#          default = false
#
#     pytest.ini config file
#   - $2 - the path to the *.ini config file, defaults to pytest.ini
#
# Exported variables in the setup.sh file: HOST_ARTIFACTS, ROOT_VENV, TEST_VENV, COPIED_PROJECT_PATH

clear_cache="${1:-false}"
INI_CONFIG_FILE="${2:-pytest.ini}"

set -Eeuo pipefail
trap cleanup EXIT ERR SIGINT SIGTERM

dockerCleanedUp=""
cleanup() {
  if [ -z "$dockerCleanedUp" ]; then
    echo "Cleaning docker setup..."
    docker compose down -v --remove-orphans
    dockerCleanedUp="clean"
  fi
# Uncomment lines from below when running tests without Docker
#  if [ -n "${VIRTUAL_ENV-}" ] && [ "$(type -t deactivate 2>/dev/null)" = "function" ]; then
#    echo "Deactivating venv..."
#    deactivate
#  fi
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
    docker compose build ui_tests_pw --no-cache
    ;;
  *)
    echo "Cache will be preserved when starting the service"
    docker compose build ui_tests_pw
esac

echo "Starting the tests..."
TEST_GREP="--ini-config $INI_CONFIG_FILE"
# If you need to run particular test(s), then set it as shown in the line below (TEST_GREP);
# to run all tests, just set TEST_GREP="$TEST_GREP" (to preserve base settings)
TEST_GREP="$TEST_GREP -k test_excel_import_page_renders_for_admin"

docker compose run -e TEST_GREP="$TEST_GREP" --rm ui_tests_pw

if [[ ! -f "$INI_CONFIG_FILE" ]]; then
  echo "ERROR: Provided path '$INI_CONFIG_FILE' for the repo does not exist"
  exit 1
else
  echo "Using $INI_CONFIG_FILE ini config file"
fi

#
#
#
