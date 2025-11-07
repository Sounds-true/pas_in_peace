# PAS Bot - Setup Guide для Mac

**Дата:** 2025-11-05
**Система:** macOS (твой Mac)

---

## 🚀 Quick Start (автоматический setup)

### Один скрипт для всего:

```bash
cd /Users/aleks/Documents/PAS_Bot
chmod +x setup_mac.sh
./setup_mac.sh
```

Этот скрипт сделает всё автоматически!

---

## 📋 Manual Setup (если хочешь понять каждый шаг)

### 1. PostgreSQL и Redis уже установлены ✅

```bash
# Проверить статус
brew services list

# Если не запущены, запустить:
brew services start postgresql@15
brew services start redis
```

### 2. Создать виртуальное окружение

```bash
cd /Users/aleks/Documents/PAS_Bot
python3 -m venv venv
source venv/bin/activate
```

### 3. Установить Python зависимости

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Это займет 2-3 минуты. Установит:
- LangChain, LangGraph
- NeMo Guardrails
- Transformers, PyTorch
- PostgreSQL drivers
- И еще ~40 пакетов

### 4. Загрузить языковые модели

```bash
python -m spacy download ru_core_news_sm
```

### 5. Настроить .env файл

```bash
cp .env.example .env
nano .env  # или code .env в VS Code
```

**Обязательные ключи:**
```env
TELEGRAM_BOT_TOKEN=получить_от_@BotFather
OPENAI_API_KEY=получить_от_OpenAI
```

#### Как получить Telegram Bot Token:
1. Открыть [@BotFather](https://t.me/BotFather) в Telegram
2. Отправить `/newbot`
3. Следовать инструкциям (имя бота, username)
4. Скопировать токен типа: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

#### Как получить OpenAI API Key:
1. Зайти на [platform.openai.com](https://platform.openai.com)
2. API Keys → Create new secret key
3. Скопировать ключ типа: `sk-proj-...`

**Остальные ключи (можно оставить по умолчанию):**
```env
DATABASE_URL=postgresql+asyncpg://postgres@localhost/pas_bot
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=сгенерировать_рандомный_ключ
PII_ENCRYPTION_KEY=сгенерировать_другой_ключ
```

Сгенерировать ключи:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 6. Создать базу данных

```bash
createdb pas_bot
```

### 7. Запустить миграции

```bash
alembic upgrade head
```

### 8. Запустить бота!

```bash
python main.py
```

Должен вывести:
```
bot_initialized environment="development"
bot_starting mode="polling"
bot_running mode="polling"
```

### 9. Протестировать в Telegram

1. Найти бота по username
2. Отправить `/start`
3. Бот должен ответить приветствием! 🎉

---

## 🔧 Troubleshooting

### Проблема: "command not found: createdb"

```bash
# Добавить PostgreSQL в PATH
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Или для старого Mac (Intel):
echo 'export PATH="/usr/local/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Проблема: "redis-cli not found"

```bash
# Добавить Redis в PATH
echo 'export PATH="/opt/homebrew/opt/redis/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Проблема: "ModuleNotFoundError"

```bash
# Убедиться что venv активирован
source venv/bin/activate

# Переустановить зависимости
pip install -r requirements.txt --force-reinstall
```

### Проблема: "Database connection error"

```bash
# Проверить что PostgreSQL работает
brew services list | grep postgresql
pg_isready

# Если не работает, перезапустить
brew services restart postgresql@15
```

### Проблема: PyTorch/Transformers медленно грузятся

- Это нормально! Первый раз скачивает ~1-2GB моделей
- Потом будут кэшироваться

---

## 🛠️ Полезные команды

### Управление сервисами:

```bash
# Запустить PostgreSQL и Redis
brew services start postgresql@15
brew services start redis

# Остановить
brew services stop postgresql@15
brew services stop redis

# Перезапустить
brew services restart postgresql@15
brew services restart redis

# Статус
brew services list
```

### Управление базой данных:

```bash
# Подключиться к БД
psql pas_bot

# Команды в psql:
\dt              # Показать таблицы
\d users         # Структура таблицы users
\q               # Выйти

# Удалить и пересоздать БД (если нужно)
dropdb pas_bot
createdb pas_bot
alembic upgrade head
```

### Управление Redis:

```bash
# Подключиться к Redis
redis-cli

# Команды в redis-cli:
PING             # Должно вернуть PONG
KEYS *           # Показать все ключи
FLUSHALL         # Очистить всё (осторожно!)
quit             # Выйти
```

### Запуск бота:

```bash
# В режиме разработки (с логами)
python main.py

# В debug mode (больше логов)
LOG_LEVEL=DEBUG python main.py

# Или через Makefile
make run
make run-debug
```

### Тесты:

```bash
# Запустить тесты
pytest

# С coverage
pytest --cov=src

# Конкретный тест
pytest tests/test_config.py -v
```

---

## 📊 Мониторинг

### Логи бота:

```bash
# Логи в реальном времени
tail -f data/logs/*.log

# Фильтровать по level
tail -f data/logs/*.log | grep ERROR

# Фильтровать по событиям
tail -f data/logs/*.log | grep -E "crisis|emotion|pii"
```

### Логи PostgreSQL:

```bash
# Найти лог файл
psql -c "SHOW log_directory;"

# Смотреть логи
tail -f /opt/homebrew/var/log/postgresql@15.log
```

### Мониторинг Redis:

```bash
# В реальном времени
redis-cli MONITOR
```

---

## 🎯 Следующие шаги

### Готов к разработке? Начни Sprint 2:

1. Читай [NEXT_STEPS.md](/NEXT_STEPS.md)
2. Задачи в [docs/backlog/index.md](/docs/backlog/index.md)
3. Архитектура в [docs/SOURCE_OF_TRUTH.md](/docs/SOURCE_OF_TRUTH.md)

### Основные задачи Sprint 2:

1. **Интеграция эмоций:**
   - Файл: `src/nlp/emotion_detector.py`
   - Интегрировать в `src/orchestration/state_manager.py`

2. **Терапевтические техники:**
   - Создать: `src/techniques/`
   - Реализовать: CBT, grounding, validation

3. **PII protection:**
   - Активировать в `src/core/bot.py`
   - Тестировать с русскими PII

4. **UX улучшения:**
   - Добавить inline кнопки
   - Меню техник

---

## 📞 Помощь

### Документация:
- [README.md](/README.md) - Основная документация
- [QUICKSTART.md](/QUICKSTART.md) - Быстрый старт
- [docs/SOURCE_OF_TRUTH.md](/docs/SOURCE_OF_TRUTH.md) - Всё о системе

### Если что-то не работает:
1. Проверь логи: `tail -f data/logs/*.log`
2. Проверь сервисы: `brew services list`
3. Проверь .env файл
4. Перезапусти бота

---

**Статус:** Ready для разработки! 🚀
**Последнее обновление:** 2025-11-05
