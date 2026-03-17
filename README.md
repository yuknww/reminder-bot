## Reminder Bot 🤖⏰

Небольшой Telegram‑бот для создания напоминаний.  
Ты пишешь, о чём и когда напомнить, бот сохраняет это в базу и в нужный момент присылает уведомление в Telegram.

Бот использует асинхронный стек (aiogram + SQLAlchemy async) и может работать как локально, так и в контейнере Docker.

---

### Стек

- **Язык**: Python 3.12+
- **Telegram‑фреймворк**: `aiogram 3`
- **База данных**: SQLite (через `SQLAlchemy` + `aiosqlite`) или PostgreSQL (через `asyncpg`)
- **Брокер сообщений**: RabbitMQ (через `aio_pika`)
- **Конфигурация**: `.env` + `python-dotenv`
- **Контейнеризация**: `Docker` + `docker-compose`

---

### Структура проекта

- `main.py` — точка входа, инициализация бота, БД и слушателя напоминаний.
- `bot/config.py` — загрузка переменных окружения (токен бота, URL БД).
- `bot/states.py` — FSM‑состояния для сценария создания напоминаний.
- `bot/handlers/start.py` — обработчик `/start`, главное меню и просмотр напоминаний.
- `bot/handlers/remind.py` — сценарий создания напоминания (текст + дата/время).
- `bot/scheduler.py` — фоновый слушатель, который периодически проверяет БД и кладёт просроченные напоминания в очередь RabbitMQ.
- `bot/consumer.py` — consumer, который читает очередь RabbitMQ и отправляет напоминания в Telegram.
- `bot/database/db.py` — инициализация async‑движка SQLAlchemy и фабрики сессий.
- `bot/database/models.py` — модель `Reminder`.
- `bot/database/repository.py` — репозиторий для работы с напоминаниями (CRUD + выборки).
- `requirements.txt` — зависимости проекта.
- `Dockerfile` — образ приложения.

---

### Переменные окружения

Создай файл `.env` в корне проекта и укажи в нём:

```env
BOT_TOKEN=твой_telegram_bot_token

# Необязательно. Если не указать, используется SQLite-файл reminders.db в корне проекта.
DATABASE_URL=sqlite+aiosqlite:///./reminders.db

# RabbitMQ (обязателен для очереди напоминаний)
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

Если ты оставишь `DATABASE_URL` пустым, `main.py` автоматически подставит SQLite по умолчанию.

---

### Запуск локально (без Docker)

1. **Установи зависимости**:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

2. **Подними RabbitMQ** (например, через Docker):

```bash
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management
```

3. **Создай файл `.env`** (см. секцию выше).

4. **Запусти бота**:

```bash
python main.py
```

Бот запустится и начнёт опрашивать Telegram API. Напоминания будут храниться в `reminders.db` в корне проекта.

---

### Запуск через Docker

В репозитории уже есть `Dockerfile` и `docker-compose.yml`, поэтому удобнее запускать всё через compose.

1. **Создай `.env` в корне проекта**:

```env
BOT_TOKEN=твой_telegram_bot_token

# PostgreSQL для docker-compose
POSTGRES_USER=reminder
POSTGRES_PASSWORD=reminder
POSTGRES_DB=reminder
DATABASE_URL=postgresql+asyncpg://reminder:reminder@db:5432/reminder

# RabbitMQ для docker-compose
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
```

2. **Запусти сервисы**:

```bash
docker compose up -d --build
```

Пояснения:

- `db` — PostgreSQL (данные в volume `postgres_data`);
- `rabbitmq` — брокер сообщений (UI доступен на `http://localhost:15672`, логин/пароль `guest/guest`);
- `bot` — Telegram‑бот.

---

### Как пользоваться ботом

1. Найди своего бота в Telegram (через `@username`, который ты указал в BotFather).
2. Напиши `/start`:
   - бот поприветствует тебя и покажет клавиатуру:
     - **📝 Создать напоминание**
     - **📋 Мои напоминания**
3. Нажми **📝 Создать напоминание** или используй команду `/remind`:
   - введи текст напоминания;
   - затем введи дату и время в формате `ДД.ММ.ГГГГ ЧЧ:ММ` (например, `25.12.2025 18:00`).
4. Когда наступит время, бот пришлёт тебе дружелюбное сообщение с напоминанием.
5. Через кнопку **📋 Мои напоминания** можно посмотреть последние созданные напоминания и их статусы.

---

### Внутреннее устройство (коротко)

- При запуске:
  - инициализируется БД через SQLAlchemy;
  - создаются таблицы (если их ещё нет);
  - запускается фоновая корутина‑слушатель напоминаний, публикующая задачи в RabbitMQ;
  - запускается consumer, который отправляет напоминания из очереди;
  - aiogram‑диспетчер начинает принимать апдейты от Telegram.
- При создании напоминания:
  - данные проходят через FSM (`Form.waiting_for_remind` → `Form.waiting_for_date`);
  - бот валидирует формат даты и проверяет, что дата в будущем;
  - напоминание сохраняется в БД со статусом `pending`.
- Фоновый слушатель (`bot/scheduler.py`):
  - периодически (раз в несколько секунд) выбирает просроченные `pending`‑напоминания;
  - складывает их в очередь `reminders` в RabbitMQ.
- Consumer (`bot/consumer.py`):
  - читает очередь `reminders`;
  - отправляет сообщения пользователям и помечает напоминания как `sent`.

---

### Идеи для дальнейшего развития

- Вынести consumer в отдельный процесс/контейнер для масштабирования.
- Добавить редактирование и удаление напоминаний.
- Добавить многоязычную поддержку (RU/EN) и переключение языка.
