#!/bin/zsh
set -euo pipefail

cd "$(dirname "$0")/.."

cleanup() {
  docker compose down -v --remove-orphans >/dev/null 2>&1 || true
}

trap cleanup EXIT

docker compose up --build -d

for _ in {1..60}; do
  if curl -s http://127.0.0.1:3000/health >/dev/null 2>&1; then
    npx playwright test
    exit $?
  fi
  sleep 2
done

echo "Timed out waiting for the demo stack to become healthy." >&2
exit 1
