#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

docker compose up -d --wait db
docker compose run --build --rm backend alembic upgrade head
