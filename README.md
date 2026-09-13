# Habit Tracker API

REST API для трекера привычек на FastAPI. Пользователь может зарегистрироваться, войти в систему, управлять своими привычками и отмечать их выполнение с учётом периодичности и часового пояса.

> Проект находится в разработке. Основная бизнес-логика и авторизация реализованы, автоматические тесты и статистика пока запланированы.

## Что реализовано

- регистрация и вход пользователя;
- короткоживущий access JWT;
- refresh token в `HttpOnly` cookie;
- ротация и отзыв refresh-токенов;
- получение данных текущего пользователя;
- CRUD привычек с проверкой владельца;
- отметки выполнения привычек;
- периоды `daily`, `weekly` и `monthly`;
- расчёт границ периода в часовом поясе пользователя;
- PostgreSQL, асинхронный SQLAlchemy и миграции Alembic;
- запуск приложения через Docker Compose;
- интерактивная документация Swagger UI и ReDoc.

## Стек

`Python 3.13` · `FastAPI` · `SQLAlchemy 2.0` · `PostgreSQL 17` · `asyncpg` · `Alembic` · `Pydantic` · `PyJWT` · `Argon2` · `Docker Compose` · `uv`

## Быстрый запуск через Docker

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/Avaron23/habit-tracker-API.git
cd habit-tracker-API
```

### 2. Создайте файл с переменными окружения

```bash
cp .env.example .env
```

Для PowerShell:

```powershell
Copy-Item .env.example .env
```

Замените тестовые значения в `.env`. Для Docker адрес базы данных должен содержать имя сервиса `db`:

```env
DATABASE_URL="postgresql+asyncpg://postgres:password@db:5432/habit_db"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="password"
POSTGRES_DB="habit_db"
SECRET_KEY="replace-with-a-long-random-secret"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
SECURE_COOKIE=false
```

Сгенерировать `SECRET_KEY` можно командой:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 3. Запустите контейнеры и примените миграции

```bash
docker compose up --build -d
docker compose exec backend alembic upgrade head
```

После запуска доступны:

- API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## Как пользоваться API

### 1. Зарегистрируйтесь

`POST /auth/register`

```json
{
  "username": "Avaron",
  "password": "strong-password",
  "timezone": "Europe/Moscow"
}
```

Поддерживаемые часовые пояса: `Europe/Moscow`, `UTC` и `America/New_York`.

### 2. Получите access token

`POST /auth/login` принимает данные формы `application/x-www-form-urlencoded`:

```bash
curl -c cookies.txt -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=Avaron&password=strong-password"
```

Access token возвращается в теле ответа, refresh token устанавливается в `HttpOnly` cookie.

### 3. Авторизуйте защищённые запросы

```http
Authorization: Bearer <access_token>
```

В Swagger UI нажмите **Authorize** и вставьте access token.

### 4. Создайте привычку

`POST /habits/`

```json
{
  "title": "Read",
  "description": "Read every day",
  "goal": 1,
  "period": "daily"
}
```

### 5. Отметьте выполнение

```http
POST /habitlogs/{habit_id}
```

Сейчас для одной привычки разрешена одна отметка в пределах её текущего периода.

## Основные endpoints

| Метод | Endpoint | Назначение | Авторизация |
| --- | --- | --- | --- |
| `POST` | `/auth/register` | Регистрация | Нет |
| `POST` | `/auth/login` | Вход и выдача токенов | Нет |
| `POST` | `/auth/refresh` | Обновление пары токенов | Refresh cookie |
| `POST` | `/auth/logout` | Отзыв refresh token | Refresh cookie |
| `GET` | `/users/me` | Текущий пользователь | Bearer token |
| `POST` | `/habits/` | Создать привычку | Bearer token |
| `GET` | `/habits/` | Получить свои привычки | Bearer token |
| `GET` | `/habits/{habit_id}` | Получить привычку | Bearer token |
| `PUT` | `/habits/{habit_id}` | Полностью обновить привычку | Bearer token |
| `DELETE` | `/habits/{habit_id}` | Удалить привычку | Bearer token |
| `POST` | `/habitlogs/{habit_id}` | Отметить выполнение | Bearer token |
| `GET` | `/habitlogs/{habit_id}` | Получить историю выполнений | Bearer token |

Полные схемы запросов и ответов доступны в Swagger UI.

## Как устроена авторизация

- Access token — JWT с ограниченным сроком действия. Клиент передаёт его в заголовке `Authorization`.
- Refresh token — случайная непрозрачная строка в `HttpOnly` cookie. В базе хранится только её SHA-256-хеш.
- При обновлении старый refresh token отзывается, после чего создаётся новый.
- При выходе текущий refresh token отзывается, а cookie удаляется.
- Уже выданный access token после выхода действует до истечения своего срока.

Для локального HTTP используется `SECURE_COOKIE=false`. В production с HTTPS необходимо установить `SECURE_COOKIE=true`.

## Структура проекта

```text
app/
├── api/            # HTTP-маршруты
├── core/           # конфигурация и функции безопасности
├── db/             # engine, сессии и базовый класс моделей
├── dependencies/   # зависимости FastAPI
├── models/         # SQLAlchemy-модели
├── schemas/        # Pydantic-схемы
├── services/       # бизнес-логика
└── alembic/        # миграции базы данных
```

Связи основных сущностей:

```text
User 1 ── N Habit
User 1 ── N RefreshToken
Habit 1 ── N HabitLog
```

Удаление пользователя каскадно удаляет его привычки и refresh-токены. Удаление привычки удаляет связанные отметки выполнения.

## Локальный запуск без Docker

Нужны Python 3.13+, `uv` и доступный PostgreSQL.

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Если PostgreSQL запущен из этого Compose-файла, локальное приложение подключается к нему через порт `15432`:

```env
DATABASE_URL="postgresql+asyncpg://postgres:password@127.0.0.1:15432/habit_db"
```

## Работа с миграциями

В `docker-compose.yml` база данных доступна:

- контейнеру backend — по адресу `db:5432`;
- локальным командам Windows, macOS или Linux — по адресу `127.0.0.1:15432`.

Поэтому миграции создаются локально с временно переопределённым `DATABASE_URL`.

### Создание миграции в PowerShell

1. Запустите PostgreSQL-контейнер:

```powershell
docker compose up -d db
```

2. Временно укажите адрес базы, доступный с локальной машины:

```powershell
$env:DATABASE_URL = "postgresql+asyncpg://postgres:password@127.0.0.1:15432/habit_db"
```

Логин, пароль и имя базы должны совпадать со значениями в `.env`.

3. Создайте миграцию и примените её:

```powershell
uv run alembic revision --autogenerate -m "describe schema change"
uv run alembic upgrade head
```

4. Удалите временную переменную из текущей сессии PowerShell:

```powershell
Remove-Item Env:DATABASE_URL
```

### Создание миграции в macOS или Linux

```bash
docker compose up -d db
DATABASE_URL="postgresql+asyncpg://postgres:password@127.0.0.1:15432/habit_db" \
  uv run alembic revision --autogenerate -m "describe schema change"
DATABASE_URL="postgresql+asyncpg://postgres:password@127.0.0.1:15432/habit_db" \
  uv run alembic upgrade head
```

Перед применением проверяйте автоматически созданный файл в `app/alembic/versions/` и добавляйте его в коммит вместе с изменением моделей.

Если после локального создания миграции вы хотите применить её из backend-контейнера, сначала пересоберите образ: в проекте нет bind mount с исходным кодом, поэтому уже запущенный контейнер не увидит новый файл.

```bash
docker compose up --build -d backend
docker compose exec backend alembic upgrade head
```

> `app/db/init_db.py` удаляет все таблицы и предназначен только для локальных экспериментов. Для изменения схемы используйте Alembic.

## Сброс локальной базы

```bash
docker compose down -v
docker compose up --build -d
docker compose exec backend alembic upgrade head
```

Команда удаляет локальный PostgreSQL volume вместе со всеми данными.

## Автор

[Avaron23](https://github.com/Avaron23)

## Статус и планы

Проект находится в активной разработке. Основные сценарии работы с пользователями, привычками и отметками выполнения уже реализованы.

Следующие шаги:

- добавить автоматические тесты для авторизации, привычек и пользовательской изоляции;
- проверить граничные случаи периодов и часовых поясов;
- автоматизировать очистку истёкших refresh-токенов;
- добавить завершение всех пользовательских сессий через `logout all`;
- реализовать статистику, текущие и максимальные серии выполнений;
- расширить список поддерживаемых часовых поясов;
- настроить CI для автоматического запуска проверок и тестов.

Цель проекта — постепенно довести API до законченного сервиса, который можно развернуть и использовать как backend полноценного веб-приложения для отслеживания привычек.