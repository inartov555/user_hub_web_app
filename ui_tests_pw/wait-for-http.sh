#!/usr/bin/env bash
set -e

URL="${1:-http://localhost:5173}"
TIMEOUT="${2:-180}"

echo "Waiting for $URL for up to ${TIMEOUT}s..."
end=$((SECONDS+TIMEOUT))
until curl -sSf "$URL" >/dev/null 2>&1; do
  if [ $SECONDS -ge $end ]; then
    echo "Timed out waiting for $URL"
    exit 1
  fi
  sleep 2
done

echo "✅ $URL is up"
