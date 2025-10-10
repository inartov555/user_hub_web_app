#!/bin/bash

# Input parameters:
#   - $1: the path to the *.ini config file, defaults to pytest.ini
# Exported variables in the setup.sh file: HOST_ARTIFACTS, ROOT_VENV, TEST_VENV, COPIED_PROJECT_PATH

ORIGINAL_PROJECT_PATH="$(pwd)"
eval source ./setup.sh
if [[ $? -ne 0 ]]; then
  return 1
fi

DEFAULT_INI_CONFIG_FILE="pytest.ini"
if [[ -z "$1" ]]; then
  echo "WARNING: no path passed for the project, defaulting to $DEFAULT_INI_CONFIG_FILE"
  INI_CONFIG_FILE="$DEFAULT_INI_CONFIG_FILE"
  if [[ ! -f "$INI_CONFIG_FILE" ]]; then
    echo "ERROR: Default path $DEFAULT_INI_CONFIG_FILE for the repo does not exist"
    return 1
  fi
elif [[ ! -d "$1" ]]; then
  echo "ERROR: Provided path '$2' for the repo does not exist"
  return 1
else
  INI_CONFIG_FILE="$1"
  echo "Using $INI_CONFIG_FILE ini config file"
fi

python3 -m pytest -v --tb=short -s --reruns 2 --reruns-delay 2 --ini-config "$INI_CONFIG_FILE" --html=$HOST_ARTIFACTS/test_report_$(date +%Y-%m-%d_%H-%M-%S).html
# Now, let's deactivate venv
deactivate
# Returning to the original project path to be able to run the test again with new changes, if there are any
cd "$ORIGINAL_PROJECT_PATH"
