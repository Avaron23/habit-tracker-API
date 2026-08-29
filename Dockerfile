FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

ENV UV_NO_DEV=1
RUN uv sync --frozen 

COPY . .

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["uv", "run" ,"uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]