# Habit Tracker API

Backend API для трекера привычек. Проект позволяет пользователям регистрироваться, входить в систему, создавать привычки и отмечать их выполнение.

## Возможности

- регистрация пользователей;
- авторизация через access JWT;
- refresh token в HttpOnly cookie;
- ротация refresh token;
- отзыв refresh token при logout;
- просмотр текущего пользователя;
- создание, получение, изменение и удаление привычек;
- проверка принадлежности привычек текущему пользователю;
- создание и получение логов выполнения привычек;
- ограничение повторных логов в рамках периода привычки;
- поддержка периодов `daily`, `weekly` и `monthly`;
- учёт часового пояса пользователя;
- каскадное удаление связанных записей;
- PostgreSQL и асинхронный SQLAlchemy;
- Alembic для миграций базы данных;
- автоматическая OpenAPI-документация через Swagger UI.

## Стек

- Python 3.13+;
- FastAPI;
- Uvicorn;
- PostgreSQL 17;
- SQLAlchemy 2 с async API;
- asyncpg;
- Pydantic Settings;
- PyJWT;
- pwdlib с Argon2;
- uv как менеджер зависимостей.

## Структура проекта

```text
app/
├── api/              # HTTP-маршруты FastAPI
├── core/             # конфигурация и security-функции
├── db/               # engine и сессии базы данных
├── alembic/          # конфигурация и версии миграций
├── dependencies/     # FastAPI dependencies, включая текущего пользователя
├── models/           # SQLAlchemy-модели
├── schemas/          # Pydantic-схемы запросов и ответов
└── services/         # бизнес-логика

Dockerfile
docker-compose.yml
alembic.ini
pyproject.toml
uv.lock
```

## Требования

Для локального запуска нужны:

- Python 3.13 или новее;
- PostgreSQL 17 или запущенный PostgreSQL-контейнер;
- uv.

Для Docker-запуска нужны:

- Docker;
- Docker Compose.

## Переменные окружения

Скопируйте `.env.example` в `.env` и задайте значения:

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

Описание переменных:

| Переменная | Назначение |
| --- | --- |
| `DATABASE_URL` | Async URL подключения к PostgreSQL |
| `POSTGRES_USER` | Пользователь PostgreSQL |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL |
| `POSTGRES_DB` | Имя базы данных |
| `SECRET_KEY` | Секрет для подписи access JWT |
| `ALGORITHM` | Алгоритм подписи JWT, например `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни access token в минутах |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Время жизни refresh token в днях |
| `SECURE_COOKIE` | Требовать HTTPS для refresh cookie |

Для локального запуска через обычный HTTP установите `SECURE_COOKIE=false`. В production с HTTPS установите `SECURE_COOKIE=true`.

Для Docker используйте hostname `db` и внутренний порт PostgreSQL `5432`. Для запуска Alembic с Windows через проброшенный порт используйте временный URL с `127.0.0.1:15432`.

Не добавляйте настоящий `.env` в Git. Он уже указан в `.gitignore`.

## Запуск через Docker Compose

Создайте `.env`, затем выполните первый запуск:

```powershell
docker compose up --build -d
docker compose exec backend alembic upgrade head
```

Команда `alembic upgrade head` применяет все миграции и создаёт таблицы в PostgreSQL.

После запуска API должен быть доступен по адресу:

```text
http://localhost:8000
```

Документация:

```text
http://localhost:8000/docs
http://localhost:8000/redoc
```

### Передача конфигурации в Docker

Docker Compose передаёт настройки явно и разделяет их между сервисами:

- `backend` получает `DATABASE_URL`, настройки JWT, сроки действия токенов и параметр `SECURE_COOKIE`;
- `db` получает `POSTGRES_USER`, `POSTGRES_PASSWORD` и `POSTGRES_DB`.

Внутри `DATABASE_URL` для Docker должен использоваться hostname `db`, потому что это имя PostgreSQL-сервиса в Compose:

```env
DATABASE_URL="postgresql+asyncpg://postgres:password@db:5432/habit_db"
```

Не добавляйте настоящий `.env` в Docker image. Compose читает его на хосте и передаёт необходимые значения контейнерам через конфигурацию сервисов.

Порт PostgreSQL проброшен на хост как `15432:5432`:

- внутри Docker: `db:5432`;
- с Windows: `127.0.0.1:15432`.

### Перезапуск контейнеров

Для обычного перезапуска без удаления данных используйте:

```powershell
docker compose down
docker compose up -d
```

PostgreSQL volume при этом сохраняется.

### Полный сброс базы данных

Если нужна полная пересборка локальной базы после изменения схемы:

```powershell
docker compose down -v
docker compose up --build -d
docker compose exec backend alembic upgrade head
```

Флаг `-v` удаляет PostgreSQL volume вместе со всеми данными. Используйте эту команду только для локальной разработки, когда данные не нужны.

## Локальный запуск

Установите зависимости:

```powershell
uv sync
```

Убедитесь, что PostgreSQL запущен и `DATABASE_URL` указывает на него. Если PostgreSQL запущен через Compose, локальный URL должен использовать `127.0.0.1:15432`:

```env
DATABASE_URL="postgresql+asyncpg://postgres:password@127.0.0.1:15432/habit_db"
```

Затем запустите API:

```powershell
uv run uvicorn app.main:app --reload
```

API будет доступен по адресу `http://localhost:8000`.

## Миграции базы данных

Схема базы данных управляется Alembic. Первая миграция создаёт таблицы `users`, `habits`, `habit_logs` и `refresh_tokens`, а также индексы и каскадные внешние ключи.

Для применения уже созданных миграций внутри Docker:

```powershell
docker compose exec backend alembic upgrade head
```

Для создания новой миграции после изменения SQLAlchemy-моделей:

1. Запустите PostgreSQL:

	```powershell
	docker compose up -d
	```

2. Временно укажите URL для запуска Alembic с Windows:

	```powershell
	$env:DATABASE_URL = "postgresql+asyncpg://postgres:password@127.0.0.1:15432/habit_db"
	```

3. Создайте миграцию из корня проекта:

	```powershell
	uv run alembic revision --autogenerate -m "describe schema change"
	```

4. Удалите временную переменную:

	```powershell
	Remove-Item Env:DATABASE_URL
	```

5. Проверьте созданный файл в `app/alembic/versions/`, пересоберите backend и примените миграцию:

	```powershell
	docker compose up --build -d
	docker compose exec backend alembic upgrade head
	```

Миграционный файл нужно коммитить вместе с изменением модели. Не запускайте `app/db/init_db.py` для обычного обновления схемы: этот legacy-скрипт удаляет все таблицы через `drop_all()` и предназначен только для локальных экспериментов.

## Авторизация

В проекте используются два токена.

### Access token

Access token — короткоживущий JWT. Он возвращается в ответе login и передаётся в защищённые запросы через заголовок:

```http
Authorization: Bearer <access_token>
```

Сервер проверяет подпись, срок действия и идентификатор пользователя из claim `sub`.

### Refresh token

Refresh token — случайная непрозрачная строка, а не JWT. Клиент получает его через HttpOnly cookie. В базе хранится только SHA-256 хеш refresh token.

При обновлении:

1. сервер читает refresh cookie;
2. хеширует полученное значение;
3. ищет запись в базе;
4. проверяет срок действия и `revoked`;
5. отзывает старый refresh token;
6. создаёт новую пару токенов;
7. устанавливает новую refresh cookie.

Logout отзывает текущий refresh token и удаляет cookie. Уже выданный access token продолжает работать до истечения своего срока действия.

## API endpoints

Все endpoints habits, habit logs и `/users/me` требуют access token. `/auth/refresh` и `/auth/logout` используют refresh cookie и не требуют access token.

### Auth

#### `POST /auth/register`

Создаёт пользователя.

Тело запроса:

```json
{
	"username": "Avaron",
	"password": "strong-password",
	"timezone": "Europe/Moscow"
}
```

Допустимые часовые пояса сейчас:

- `Europe/Moscow`;
- `UTC`;
- `America/New_York`.

Пароль сохраняется только в виде Argon2-хеша.

#### `POST /auth/login`

Выполняет вход и возвращает access token. Endpoint принимает `application/x-www-form-urlencoded`, а не JSON.

Поля формы:

```text
username=Avaron
password=strong-password
```

Пример через curl:

```powershell
curl.exe -X POST http://localhost:8000/auth/login `
	-H "Content-Type: application/x-www-form-urlencoded" `
	-d "username=Avaron&password=strong-password"
```

Ответ:

```json
{
	"access_token": "eyJ...",
	"token_type": "bearer",
	"expires_in": 1800
}
```

В ответе также устанавливается cookie `refresh_token`.

#### `POST /auth/refresh`

Получает refresh token из cookie и возвращает новый access token. Старый refresh token отзывается, а cookie заменяется новой.

Для ручного тестирования через Swagger убедитесь, что браузер сохранил cookie после login. Для curl используйте cookie-файл:

```powershell
curl.exe -c cookies.txt -X POST http://localhost:8000/auth/login `
	-H "Content-Type: application/x-www-form-urlencoded" `
	-d "username=Avaron&password=strong-password"

curl.exe -b cookies.txt -c cookies.txt -X POST http://localhost:8000/auth/refresh
```

#### `POST /auth/logout`

Отзывает refresh token из cookie и удаляет cookie у клиента.

```powershell
curl.exe -b cookies.txt -c cookies.txt -X POST http://localhost:8000/auth/logout
```

Access token после logout не отзывается мгновенно и остаётся действительным до истечения срока.

### Users

#### `GET /users/me`

Возвращает текущего пользователя. Требует заголовок:

```http
Authorization: Bearer <access_token>
```

### Habits

Все endpoints habits требуют access token.

#### `POST /habits/`

Создаёт привычку текущего пользователя. `user_id` не передаётся клиентом.

```json
{
	"title": "Read",
	"description": "Read every day",
	"goal": 1,
	"period": "daily"
}
```

Допустимые значения `period`: `daily`, `weekly`, `monthly`.

#### `GET /habits/`

Возвращает список привычек текущего пользователя.

#### `GET /habits/{habit_id}`

Возвращает одну привычку, если она принадлежит текущему пользователю. Для чужой или несуществующей привычки возвращается `404`.

#### `PUT /habits/{habit_id}`

Полностью заменяет данные привычки. Тело запроса использует ту же схему, что и создание.

#### `DELETE /habits/{habit_id}`

Удаляет привычку текущего пользователя. Связанные habit logs удаляются каскадно на уровне базы данных.

### Habit logs

Все endpoints habit logs требуют access token.

#### `POST /habitlogs/{habit_id}`

Создаёт лог выполнения привычки, если привычка принадлежит текущему пользователю и в текущем периоде ещё нет лога.

Период определяется с учётом часового пояса пользователя:

- `daily` — календарный день пользователя;
- `weekly` — календарная неделя с понедельника;
- `monthly` — календарный месяц.

Повторное выполнение в том же периоде возвращает ошибку `400`.

#### `GET /habitlogs/{habit_id}`

Возвращает все логи привычки текущего пользователя, отсортированные от новых к старым.

Для чужой или несуществующей привычки возвращается `404`.

## Проверка через Swagger

1. Запустите API.
2. Откройте `http://localhost:8000/docs`.
3. Выполните `/auth/register`.
4. Выполните `/auth/login` через form-data.
5. Нажмите `Authorize` и вставьте access token, если Swagger не заполнил его автоматически.
6. Вызовите `/users/me`.
7. Создайте привычку через `POST /habits/`.
8. Создайте лог через `POST /habitlogs/{habit_id}`.
9. Получите логи через `GET /habitlogs/{habit_id}`.

Refresh cookie браузер отправляет автоматически, если запросы выполняются с подходящими настройками cookie. При локальном HTTP должен быть установлен `SECURE_COOKIE=false`.

## Модель данных

Основные связи:

```text
User 1 --- N Habit
User 1 --- N RefreshToken
Habit 1 --- N HabitLog
```

Внешние ключи habits и refresh tokens используют каскадное удаление:

- удаление пользователя удаляет его habits и refresh tokens;
- удаление habit удаляет связанные habit logs.

## Тестирование и проверки

Сейчас проект содержит базовые проверки компиляции и запуска приложения:

```powershell
uv run python -m compileall -q app
uv run uvicorn app.main:app --reload
```

Автоматические тесты пока не добавлены. Перед production-использованием нужно протестировать:

- регистрацию и повторный username;
- правильный и неправильный login;
- истечение access token;
- refresh rotation;
- повторное использование отозванного refresh token;
- logout;
- изоляцию привычек и логов между пользователями;
- границы daily/weekly/monthly периодов;
- каскадное удаление.

## Текущие ограничения

- отдельного `logout all` пока нет;
- очистка старых и отозванных refresh tokens пока не автоматизирована;
- access token после logout действует до своего истечения;
- `init_db.py` остаётся legacy-скриптом и удаляет существующие таблицы;
- автоматические тесты пока отсутствуют;
- статистика по привычкам пока не реализована.

## Дальнейшее развитие

Приоритетные следующие шаги:

1. добавить автоматические тесты для auth, habits и habit logs;
2. добавить очистку истёкших refresh tokens;
3. добавить `logout all` при необходимости;
4. добавить статистику и серии выполнения привычек;
5. расширить список поддерживаемых часовых поясов.
