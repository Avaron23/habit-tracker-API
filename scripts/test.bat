@echo off
setlocal
cd /d "%~dp0.."

set "COMPOSE_FILE=docker-compose.test.yml"
set "DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:15433/habit_test_db"
set "TEST_DATABASE_URL=%DATABASE_URL%"
set "EXIT_CODE=0"

docker compose -f "%COMPOSE_FILE%" down
if errorlevel 1 exit /b %ERRORLEVEL%

docker compose -f "%COMPOSE_FILE%" up --build -d --wait
if errorlevel 1 (
    set "EXIT_CODE=1"
    goto cleanup
)

uv run alembic upgrade head
if errorlevel 1 (
    set "EXIT_CODE=1"
    goto cleanup
)

uv run pytest --cov=app --cov-report=term-missing --cov-fail-under=70
if errorlevel 1 set "EXIT_CODE=1"

:cleanup
docker compose -f "%COMPOSE_FILE%" down
if errorlevel 1 if "%EXIT_CODE%"=="0" set "EXIT_CODE=1"
exit /b %EXIT_CODE%
