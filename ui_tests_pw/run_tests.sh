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

if [[ ! -f "$INI_CONFIG_FILE" ]]; then
  echo "ERROR: Provided ini file '$INI_CONFIG_FILE' does not exist"
  exit 1
else
  echo "Using '$INI_CONFIG_FILE' ini config file"
fi

# Copying the pytest.ini file to the project when it's outside one
rsync -aq --progress "$INI_CONFIG_FILE" "$COPIED_PROJECT_PATH/pytest.ini"
if [ $? -ne 0 ]; then
  echo "Can't copy '$INI_CONFIG_FILE'"
  exit 1
fi

# chromium chrome msedge firefox webkit

# Read browser parameter from pytest.ini and pass the value to Docker to install on the needed browser.
# If parameter is not present, then default value is taken - 'chromium'.
readFromPyestIni() {
  # Input parameters:
  # 	1. pytest.ini file path
  # 	2. Section in the pytest.ini file, e.g., pytest
  #	3. Parameter name, in this case, 'browser'
  local ini_file1="$1" section1="$2" key1="$3"
  awk -F'=' -v section="$section1" -v key="$key1" '
    $0 ~ "^[[:space:]]*\\[" section "\\][[:space:]]*$" { in_section=1; next }
    $0 ~ "^[[:space:]]*\\[.*\\][[:space:]]*$"          { in_section=0 }  # any other section
    in_section && $0 ~ "^[[:space:]]*" key "[[:space:]]*=" {
      val=$2
      sub(/^[[:space:]]*/, "", val)
      sub(/[[:space:]]*([;#].*)?$/, "", val)
      print val
      found=1
      exit 0
    }
    END { if (!found) exit 2 }
  ' "$ini_file1"
}

if BROWSER="$(readFromPyestIni $INI_CONFIG_FILE pytest browser)"; then
  if [ -z $BROWSER ]; then
    echo "browser addopt found, but it's empty, so taking default value - chromium"
    # Default value when an empty parameter is found
    BROWSER="chromium"
  else
    echo "Found browser addopt: '$BROWSER'"
  fi
else
  echo "browser addopt was not found, taking default value - chromium"
  # Default value when parameter not found
  BROWSER="chromium"
fi

echo "Building images..."
case "$clear_cache" in
  true)
    echo "Cache will be cleared when starting the service"
    docker compose build --build-arg PW_BROWSER=$BROWSER ui_tests_pw --no-cache
    ;;
  *)
    echo "Cache will be preserved when starting the service"
    docker compose build --build-arg PW_BROWSER=$BROWSER ui_tests_pw
esac

echo "Starting the tests..."
TEST_GREP=""

# TEST_GREP="$TEST_GREP --reruns 2 --reruns-delay 2"

# Uncomment if you need tests to be run in parallel (set number or auto).
# Note: there are some tests that change settings, so you can run tests in parallel only when
#       you disable them (settings are applied globally, not for a particular user, also
#       excel tests, they work with users which are saved/deleted from the same database)
# TEST_GREP="$TEST_GREP -n auto"

# If you need to run particular test(s), then set it as shown in the line below (TEST_GREP);
# to run all tests, just set TEST_GREP="$TEST_GREP" (to preserve base settings)

# TEST_GREP="$TEST_GREP -k 'test_base_demo or test_locale_demo'"
TEST_GREP="$TEST_GREP -k 'test_verify_there_are_login_and_signup_links_for_logged_in_user or test_verify_that_there_s_no_login_and_signup_links_for_logged_in_user or test_links_to_signup_and_login'"
# TEST_GREP="$TEST_GREP -k 'test_verify_that_there_s_no_login_and_signup_links_for_logged_in_user'"

docker compose run -e TEST_GREP="$TEST_GREP" --rm ui_tests_pw

#
#
#
