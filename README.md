# Habit Tracker API

REST API для трекера привычек на FastAPI. Пользователь может зарегистрироваться, войти в систему, управлять своими привычками и отмечать их выполнение с учётом периодичности и часового пояса.

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
- автоматические тесты с PostgreSQL и проверкой покрытия;
- линтинг, форматирование и CI через GitHub Actions;
- интерактивная документация Swagger UI и ReDoc.

## Стек

`Python 3.13` · `FastAPI` · `SQLAlchemy 2.0` · `PostgreSQL 17` · `asyncpg` · `Alembic` · `Pydantic Settings` · `PyJWT` · `Argon2` · `pytest` · `pytest-cov` · `Ruff` · `Docker Compose` · `uv` · `GitHub Actions`

## Быстрый старт

### Требования

- Git;
- Docker Desktop с Docker Compose (для приложения и тестовой PostgreSQL);
- Python 3.13+ и `uv` (для тестов и локальных команд Alembic).

### 1. Скачайте проект и установите зависимости

```bash
git clone https://github.com/Avaron23/habit-tracker-API.git
cd habit-tracker-API
uv sync --locked --all-groups
cp .env.example .env
```

В PowerShell вместо `cp`:

```powershell
Copy-Item .env.example .env
```

### 2. Настройте `.env`

Откройте `.env` и задайте свои значения для пользователя и пароля PostgreSQL, имени базы и `SECRET_KEY`. Файл `.env` не добавляется в Git. Адрес базы для `DATABASE_URL` внутри Docker Compose должен использовать имя сервиса `db`, а учётные данные и имя БД должны совпадать с `POSTGRES_USER`, `POSTGRES_PASSWORD` и `POSTGRES_DB`:

```env
DATABASE_URL="postgresql+asyncpg://postgres:change-me@db:5432/habit_db"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="change-me"
POSTGRES_DB="habit_db"
SECRET_KEY="replace-with-a-generated-secret"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
SECURE_COOKIE=false
```

Создайте собственный `SECRET_KEY` и не используйте примерное значение:

```bash
uv run python -c "import secrets; print(secrets.token_urlsafe(64))"
```

`DATABASE_URL` с хостом `db` предназначен для команд внутри Compose. Для локального запуска команд Alembic на компьютере нужен адрес опубликованного порта — `127.0.0.1:15432`; подробнее см. раздел «Работа с миграциями».

### 3. Примените миграции и запустите приложение

Windows:

```powershell
scripts\migrate-local.bat
docker compose up --build -d backend
```

macOS/Linux:

```bash
bash scripts/migrate-local.sh
docker compose up --build -d backend
```

Приложение и PostgreSQL останутся запущенными. Откройте:

- API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

Чтобы остановить контейнеры, не удаляя данные локальной БД:

```bash
docker compose down
```

Чтобы посмотреть логи приложения:

```bash
docker compose logs -f backend
```

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
tests/              # unit- и API-тесты
scripts/            # локальные сценарии миграций и тестов
.github/workflows/  # CI через GitHub Actions
```

Связи основных сущностей:

```text
User 1 ── N Habit
User 1 ── N RefreshToken
Habit 1 ── N HabitLog
```

Удаление пользователя каскадно удаляет его привычки и refresh-токены. Удаление привычки удаляет связанные отметки выполнения.

## Локальный запуск приложения

Backend можно запускать локально вместо контейнера, если PostgreSQL уже доступен на компьютере. Например, используйте PostgreSQL из `docker-compose.yml`:

```powershell
docker compose up -d --wait db
$env:DATABASE_URL = "postgresql+asyncpg://<POSTGRES_USER>:<POSTGRES_PASSWORD>@127.0.0.1:15432/<POSTGRES_DB>"
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

В URL укажите те же имя пользователя, пароль и базу, что заданы в `.env`. После запуска откройте <http://localhost:8000/docs>. Когда закончите, можно удалить временную переменную:

```powershell
Remove-Item Env:DATABASE_URL
```

## Работа с миграциями

В `docker-compose.yml` база данных доступна:

- контейнеру backend — по адресу `db:5432`;
- локальным командам Windows, macOS или Linux — по адресу `127.0.0.1:15432`.

Поэтому `DATABASE_URL` в `.env` использует адрес `db:5432` для контейнеров и не подходит для запуска Alembic локально. Если команда `uv run alembic ...` запускается на компьютере, временно переопределите `DATABASE_URL`, указав `127.0.0.1:15432`. Имя пользователя, пароль и базы должны совпадать с `POSTGRES_USER`, `POSTGRES_PASSWORD` и `POSTGRES_DB` из `.env`.

### Применение миграций к локальной базе

Запустите готовый сценарий из корня проекта:

```powershell
scripts\migrate-local.bat
```

В macOS или Linux:

```bash
bash scripts/migrate-local.sh
```

Сценарий дождётся готовности локального PostgreSQL и применит миграции через одноразовый backend-контейнер. Так как Alembic работает внутри Compose-сети, он использует внутренний `DATABASE_URL` из `.env` с хостом `db`; адрес `127.0.0.1:15432` ему не нужен. Сама база и её volume сохраняются. Контейнер PostgreSQL останется запущенным.

### Создание миграции

Создание миграции — отдельный шаг: сначала измените модели, затем запустите PostgreSQL и создайте файл миграции с доступным с компьютера URL базы.

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

### Применение миграций локальной командой в Windows CMD

Если запускаете Alembic напрямую через `uv` в CMD, используйте адрес хоста, а не `db:5432`:

```bat
docker compose up -d --wait db
set "DATABASE_URL=postgresql+asyncpg://<POSTGRES_USER>:<POSTGRES_PASSWORD>@127.0.0.1:15432/<POSTGRES_DB>"
uv run alembic upgrade head
set "DATABASE_URL="
```

Подставьте значения пользователя, пароля и базы из `.env`. Для создания новой миграции вместо `upgrade head` запустите `uv run alembic revision --autogenerate -m "describe schema change"`. Не запускайте `docker compose down` после этого, если хотите оставить PostgreSQL запущенным; команда `down` остановит и приложение, и базу.

### Создание миграции в macOS или Linux

```bash
docker compose up -d db
DATABASE_URL="postgresql+asyncpg://postgres:password@127.0.0.1:15432/habit_db" \
  uv run alembic revision --autogenerate -m "describe schema change"
DATABASE_URL="postgresql+asyncpg://postgres:password@127.0.0.1:15432/habit_db" \
  uv run alembic upgrade head
```

Перед применением проверяйте автоматически созданный файл в `app/alembic/versions/` и добавляйте его в коммит вместе с изменением моделей.

После создания миграции примените её к локальной базе командой `scripts\migrate-local.bat` в Windows или `bash scripts/migrate-local.sh` в macOS/Linux.

## Запуск тестов

Тестовый сценарий использует отдельный PostgreSQL из `docker-compose.test.yml` на порту `15433`. Он начинает с чистого контейнера без volume, применяет все миграции, запускает тесты и удаляет контейнер после завершения. Локальная база приложения (порт `15432` и её volume) не используется и не изменяется.

Из корня проекта запустите сценарий для своей системы:

```powershell
# Windows
scripts\test.bat

# macOS / Linux
bash scripts/test.sh
```

Сценарий запускает `pytest` с покрытием приложения и требует не менее 70%. При ошибке миграции или тестов тестовая БД тоже будет остановлена и удалена. Для запуска нужны Python 3.13+, `uv` и Docker Compose.

### Запуск pytest вручную

Обычно достаточно `scripts\test.bat` или `bash scripts/test.sh`. Если нужно запустить pytest вручную, запустите отдельную тестовую БД и задайте обе переменные окружения, чтобы Alembic и тестовые фикстуры использовали именно её:

```powershell
docker compose -f docker-compose.test.yml up -d --wait
$env:DATABASE_URL = "postgresql+asyncpg://postgres:postgres@127.0.0.1:15433/habit_test_db"
$env:TEST_DATABASE_URL = $env:DATABASE_URL
uv run alembic upgrade head
uv run pytest --cov=app --cov-report=term-missing --cov-fail-under=70
docker compose -f docker-compose.test.yml down
Remove-Item Env:DATABASE_URL
Remove-Item Env:TEST_DATABASE_URL
```

`DATABASE_URL` читает Alembic, а `TEST_DATABASE_URL` — фикстуры тестов. **Не указывайте здесь URL локальной или production-базы:** тесты очищают таблицы перед запуском и после него. Для macOS/Linux используйте готовый `scripts/test.sh`, который задаёт URL и очищает контейнер автоматически.

## Проверки кода

Проект использует Ruff и для линтинга, и для форматирования. Из корня репозитория:

```bash
uv run ruff check .
uv run ruff format --check .
```

Чтобы исправить автоматически исправимые проблемы и применить форматирование:

```bash
uv run ruff check --fix .
uv run ruff format .
```

## Непрерывная интеграция

GitHub Actions запускает workflow при push и pull request. CI устанавливает Python 3.13 и зависимости, запускает `ruff check`, проверяет форматирование командой `ruff format --check`, применяет миграции к PostgreSQL 17 и запускает тесты с порогом покрытия 70%. Изменения считаются прошедшими CI, если все эти шаги успешны.

> `app/db/init_db.py` удаляет все таблицы и предназначен только для локальных экспериментов. Для изменения схемы используйте Alembic.

## Сброс локальной базы

> Осторожно: `down -v` безвозвратно удаляет данные локальной PostgreSQL-базы.

Windows:

```bat
docker compose down -v
scripts\migrate-local.bat
docker compose up --build -d backend
```

macOS/Linux:

```bash
docker compose down -v
bash scripts/migrate-local.sh
docker compose up --build -d backend
```

Миграции создадут пустую схему заново. Команда сброса не нужна для обычного запуска тестов — у них отдельная БД.

## Автор

[Avaron23](https://github.com/Avaron23)

## Границы MVP и планы

Текущий MVP включает регистрацию и вход пользователей, работу с привычками, отметки выполнения и просмотр их истории. Также реализованы обновление и отзыв refresh-токена для текущей сессии, часовые пояса `Europe/Moscow`, `UTC` и `America/New_York`. Тесты, миграции Alembic, проверка покрытия и CI настроены.

Следующие функции не входят в текущий MVP и остаются планами на будущее:

- автоматизировать очистку истёкших refresh-токенов;
- добавить завершение всех пользовательских сессий через `logout all`;
- реализовать статистику, текущие и максимальные серии выполнений;
- расширить список поддерживаемых часовых поясов.

Цель проекта — постепенно довести API до законченного сервиса, который можно развернуть и использовать как backend полноценного веб-приложения для отслеживания привычек.