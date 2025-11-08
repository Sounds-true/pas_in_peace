# Quick Start Guide

Быстрый старт для разработки PAS Bot.

## Предварительные требования

1. **Python 3.10+**
   ```bash
   python3 --version
   ```

2. **PostgreSQL**
   ```bash
   # macOS
   brew install postgresql@15
   brew services start postgresql@15

   # Ubuntu/Debian
   sudo apt install postgresql-15
   sudo systemctl start postgresql
   ```

3. **Redis**
   ```bash
   # macOS
   brew install redis
   brew services start redis

   # Ubuntu/Debian
   sudo apt install redis-server
   sudo systemctl start redis
   ```

## Установка за 5 минут

### 1. Клонировать и настроить окружение

```bash
cd /Users/aleks/Documents/PAS_Bot

# Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установить зависимости
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Загрузить языковые модели

```bash
# spaCy для русского языка
python -m spacy download ru_core_news_sm

# spaCy для английского (опционально)
python -m spacy download en_core_web_sm
```

### 3. Настроить переменные окружения

```bash
# Скопировать пример
cp .env.example .env

# Отредактировать .env
nano .env
```

**Минимально необходимые переменные:**
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_from_@BotFather
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost/pas_bot
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=generate_random_secret_key_here
PII_ENCRYPTION_KEY=generate_another_random_key_here
```

**Как получить ключи:**

1. **Telegram Bot Token:**
   - Открыть [@BotFather](https://t.me/BotFather) в Telegram
   - Отправить `/newbot`
   - Следовать инструкциям
   - Скопировать токен

2. **OpenAI API Key:**
   - Зайти на [platform.openai.com](https://platform.openai.com)
   - Создать API key в разделе API keys

3. **Secret Keys:**
   ```bash
   # Генерация случайных ключей
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

### 4. Создать базу данных

```bash
# Создать БД
createdb pas_bot

# Запустить миграции
alembic upgrade head
```

### 5. Запустить бота

```bash
python main.py
```

Бот запустится в режиме polling и будет готов принимать сообщения!

## Проверка работоспособности

### 1. Проверить подключение к Telegram

```bash
# В логах должно появиться:
# bot_initialized environment="development"
# bot_starting mode="polling"
# bot_running mode="polling"
```

### 2. Протестировать в Telegram

1. Найти вашего бота по username
2. Отправить `/start`
3. Получить приветственное сообщение

### 3. Проверить команды

```
/start   - Начать диалог
/help    - Помощь
/crisis  - Экстренная помощь
/privacy - Конфиденциальность
```

## Структура проекта

```
PAS_Bot/
├── src/
│   ├── core/           # Основная функциональность
│   ├── safety/         # Детекция кризисов и Guardrails
│   ├── orchestration/  # LangGraph state machine
│   ├── nlp/           # Эмоции и PII защита
│   └── storage/       # База данных
├── config/
│   ├── guardrails/    # NeMo Guardrails политики
│   └── langraph/      # Граф состояний
├── tests/             # Тесты
├── main.py           # Точка входа
└── .env              # Конфигурация (НЕ коммитить!)
```

## Разработка

### Запустить тесты

```bash
pytest
```

### Форматирование кода

```bash
black src/
ruff check src/ --fix
```

### Проверка типов

```bash
mypy src/
```

### Создать миграцию БД

```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Режим отладки

Для детального логирования:

```bash
# В .env
LOG_LEVEL=DEBUG
DEBUG=True

python main.py
```

## Частые проблемы

### 1. ModuleNotFoundError

```bash
# Убедитесь, что виртуальное окружение активировано
source venv/bin/activate

# Переустановите зависимости
pip install -r requirements.txt
```

### 2. Database connection error

```bash
# Проверить, что PostgreSQL запущен
pg_isready

# Проверить DATABASE_URL в .env
# Формат: postgresql+asyncpg://user:password@host/dbname
```

### 3. Redis connection error

```bash
# Проверить, что Redis запущен
redis-cli ping
# Должен вернуть: PONG

# Проверить REDIS_URL в .env
# Формат: redis://localhost:6379/0
```

### 4. Telegram API error

```bash
# Проверить TELEGRAM_BOT_TOKEN
# Попробовать получить информацию о боте:
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe
```

### 5. Модели не загружаются

```bash
# Убедитесь, что spaCy модели установлены
python -m spacy validate

# Переустановить модели
python -m spacy download ru_core_news_sm --force
```

## Production Deployment

Для production используйте webhook mode:

```bash
# В .env
ENVIRONMENT=production
TELEGRAM_WEBHOOK_URL=https://yourdomain.com/webhook
DEBUG=False
LOG_LEVEL=INFO

python main.py
```

## Следующие шаги

1. Изучить [ARCHITECTURE.md](docs/ARCHITECTURE.md) для понимания системы
2. Прочитать IP-планы в `docs/backlog/current/`
3. Начать разработку со Sprint 2 (Emotions & Techniques)

## Поддержка

- Документация: `docs/`
- Issues: Create issue в репозитории
- Logs: `data/logs/`

---

**Готово! Бот запущен и готов к разработке.** 🚀