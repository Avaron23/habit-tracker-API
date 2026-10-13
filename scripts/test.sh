#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "$0")/.."

compose=(docker compose -f docker-compose.test.yml)
database_url="postgresql+asyncpg://postgres:postgres@127.0.0.1:15433/habit_test_db"
export DATABASE_URL="$database_url"
export TEST_DATABASE_URL="$database_url"

cleanup() {
    status=$?
    trap - EXIT
    if ! "${compose[@]}" down && [ "$status" -eq 0 ]; then
        status=1
    fi
    exit "$status"
}

trap cleanup EXIT

"${compose[@]}" down
"${compose[@]}" up --build -d --wait
uv run alembic upgrade head
uv run pytest --cov=app --cov-report=term-missing --cov-fail-under=70
