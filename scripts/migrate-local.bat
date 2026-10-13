@echo off
setlocal
cd /d "%~dp0.."

docker compose up -d --wait db
if errorlevel 1 exit /b %ERRORLEVEL%

docker compose run --build --rm backend alembic upgrade head
exit /b %ERRORLEVEL%
