#!/bin/bash

# Input parameters:
#   - NONE
# Exported variables: HOST_ARTIFACTS, ROOT_VENV, TEST_VENV, COPIED_PROJECT_PATH

# Consider that this folder is used in the project
ARTIFACTS_ROOT_FOLDER="TEST1"

REPO="$(pwd)"
echo "REPO = '$REPO'"

# Let's retrieve the project folder name from the path to the project
PROJECT_FOLDER_NAME="${REPO##*/}"

# path where workspace will be stored
# Consider that this folder is used in the project
HOST_WORKSPACE="$HOME/$ARTIFACTS_ROOT_FOLDER/workspace"
# path where artifacts will be stored
HOST_ARTIFACTS="$HOST_WORKSPACE/artifacts"
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
echo "$REPO is copied to '$COPIED_PROJECT_PATH'"

echo "Root env set up to: '$COPIED_PROJECT_PATH'"
export ROOT_VENV="$COPIED_PROJECT_PATH"
echo "Entering the '$COPIED_PROJECT_PATH' module"
cd "$COPIED_PROJECT_PATH"

echo "Copying .env file..."
cp backend/.env.example backend/.env
echo "Appending HOST_ARTIFACTS and COPIED_PROJECT_PATH path properties"
printf '\nHOST_ARTIFACTS=%s\n' "$HOST_ARTIFACTS" >> backend/.env
printf '\nCOPIED_PROJECT_PATH=%s\n' "$COPIED_PROJECT_PATH" >> backend/.env

export TEST_VENV=$(pwd)
