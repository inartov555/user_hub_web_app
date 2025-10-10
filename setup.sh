#!/bin/bash

# Input parameters:
#   - NONE
# Exported variables: HOST_ARTIFACTS, ROOT_VENV, TEST_VENV, COPIED_PROJECT_PATH

ARTIFACTS_ROOT_FOLDER="TEST1"

REPO="$(pwd)"
echo "REPO = '$REPO'"

# Let's retrieve the project folder name from the path to the project
PROJECT_FOLDER_NAME="${REPO##*/}"

# path where workspace will be stored
HOST_WORKSPACE="$HOME/$ARTIFACTS_ROOT_FOLDER/workspace"
# path where artifacts will be stored
HOST_ARTIFACTS="$HOST_WORKSPACE/artifact"
export HOST_ARTIFACTS="$HOST_ARTIFACTS"
export COPIED_PROJECT_PATH="$HOST_WORKSPACE/$PROJECT_FOLDER_NAME"

echo "Host workspace directory (copied project + logs, screenshots, etc.):"
echo "  >>> $HOST_WORKSPACE"
echo "Host artifacts directory (logs, screenshots, etc.):"
echo "  >>> $HOST_ARTIFACTS"

mkdir -p "$HOST_ARTIFACTS"
chmod a+rw -R "$HOST_ARTIFACTS"
rm -rf "$COPIED_PROJECT_PATH"
rsync -aq --progress "$REPO" "$HOST_WORKSPACE" --exclude .git --exclude *.pyc --exclude .pytest_cache
if [ $? -ne 0 ]; then
  echo "Can't create workspace '$COPIED_PROJECT_PATH', Please configure the path inside of this script"
  ls $HOST_WORKSPACE
  return 1
fi
echo "$REPO is copied to $COPIED_PROJECT_PATH"

echo "Root env set up to: $(pwd)"
export ROOT_VENV="$COPIED_PROJECT_PATH"
echo "Entering the '$COPIED_PROJECT_PATH' module"
cd "$COPIED_PROJECT_PATH"
echo "Entering the backend folder"
cd "backend"

# Activating venv

if python3 -m venv --help > /dev/null 2>&1; then
    echo "venv module is available"
else
    python3 -m pip install --user virtualenv
fi
python3 -m venv venv
. venv/bin/activate

# python -m venv .venv && source .venv/bin/activate
# pip install -r requirements.txt
# cp .env.example .env

BASE_REQ_FILE="$COPIED_PROJECT_PATH/backend/requirements.txt"
echo "Installing module requirements from '$BASE_REQ_FILE' file..."
echo ""
python3 -m pip install --upgrade pip
python3 -m pip install -r "$BASE_REQ_FILE"

echo "Virtual env set up to: $(pwd)"
export TEST_VENV=$(pwd)
