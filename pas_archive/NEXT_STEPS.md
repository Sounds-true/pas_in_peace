# 🚀 Next Steps - Что делать дальше?

**Sprint 1 завершен!** Базовая инфраструктура готова. Теперь нужно запустить и протестировать бота.

---

## ⚡ Быстрый старт (5 минут)

### 1. Настроить окружение

```bash
# Активировать виртуальное окружение (если ещё не активировано)
cd /Users/aleks/Documents/PAS_Bot
python3 -m venv venv
source venv/bin/activate

# Установить зависимости
pip install --upgrade pip
pip install -r requirements.txt

# Загрузить языковые модели
python -m spacy download ru_core_news_sm
```

### 2. Настроить .env файл

```bash
# Скопировать шаблон
cp .env.example .env

# Отредактировать (нужны минимум эти ключи)
nano .env
```

**Необходимо добавить:**
```env
TELEGRAM_BOT_TOKEN=получить_от_@BotFather
OPENAI_API_KEY=получить_от_OpenAI
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost/pas_bot
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
PII_ENCRYPTION_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

### 3. Создать базу данных

```bash
# Создать PostgreSQL базу
createdb pas_bot

# Запустить миграции
alembic upgrade head
```

### 4. Запустить бота

```bash
python main.py
```

**Готово!** Бот запущен и готов принимать сообщения в Telegram.

---

## 📋 Проверочный чек-лист

Перед тем как начать разработку Sprint 2, убедитесь что всё работает:

### Базовая функциональность
- [ ] Бот отвечает на `/start`
- [ ] Команда `/help` показывает список команд
- [ ] Команда `/crisis` показывает номера помощи
- [ ] Бот обрабатывает обычные сообщения
- [ ] Логи пишутся в `data/logs/`

### База данных
- [ ] PostgreSQL запущен (`pg_isready`)
- [ ] База `pas_bot` создана
- [ ] Миграции применены (`alembic current`)
- [ ] Таблицы созданы (можно проверить в psql)

### Redis (опционально, для продакшн)
- [ ] Redis запущен (`redis-cli ping` должен вернуть PONG)
- [ ] Подключение работает

### Safety системы
- [ ] Crisis detector загружается без ошибок
- [ ] Guardrails инициализируются
- [ ] Попробуйте кризисное сообщение и проверьте реакцию

### Тестирование
- [ ] Запустите тесты: `pytest`
- [ ] Проверьте линтер: `make lint`
- [ ] Форматирование: `make format`

---

## 🎯 Sprint 2: Что делать дальше?

### Приоритет 1: Эмоциональный анализ

**Задача:** Интегрировать GoEmotions в реальный диалог

**Файлы для работы:**
- `src/nlp/emotion_detector.py` - уже создан, нужно интегрировать
- `src/orchestration/state_manager.py` - добавить emotion detection в `_handle_emotion_check`

**Шаги:**
1. Загрузить GoEmotions модель для русского языка
2. Добавить вызов emotion detector в state_manager
3. Использовать результаты для routing transitions
4. Добавить emotion tracking в Message model

**Код для интеграции:**
```python
# В state_manager.py
from src.nlp.emotion_detector import EmotionDetector

async def _handle_emotion_check(self, state: Dict[str, Any]) -> Dict[str, Any]:
    emotion_detector = EmotionDetector()
    await emotion_detector.initialize()

    message = state["message"]
    assessment = await emotion_detector.assess_emotional_state(message)

    user_state = state["user_state"]
    user_state.emotional_score = 1.0 - assessment["distress_score"]
    user_state.crisis_level = assessment["distress_score"]

    state["emotion_assessed"] = True
    state["primary_emotion"] = assessment["primary_emotion"]

    return state
```

### Приоритет 2: Базовые терапевтические техники

**Задача:** Реализовать 3-5 простых техник

**Создать новые файлы:**
```
src/techniques/
├── __init__.py
├── base.py           # Базовый класс Technique
├── cbt.py            # Cognitive reframing
├── grounding.py      # 5-4-3-2-1 и другие
├── validation.py     # Эмпатический ответ
└── active_listening.py
```

**Пример структуры:**
```python
# src/techniques/base.py
class Technique:
    name: str
    description: str

    async def apply(self, user_message: str, context: Dict) -> str:
        raise NotImplementedError

# src/techniques/grounding.py
class GroundingTechnique(Technique):
    name = "5-4-3-2-1 Grounding"

    async def apply(self, user_message: str, context: Dict) -> str:
        return """
        Давайте попробуем технику заземления "5-4-3-2-1":

        Назовите:
        • 5 вещей, которые вы ВИДИТЕ вокруг себя
        • 4 вещи, которые вы можете ПОТРОГАТЬ
        • 3 вещи, которые вы СЛЫШИТЕ
        • 2 вещи, которые вы можете ПОНЮХАТЬ
        • 1 вещь, которую вы можете ПОПРОБОВАТЬ на вкус

        Это поможет вернуться в настоящий момент.
        """
```

### Приоритет 3: PII Protection в action

**Задача:** Активировать PII scrubbing в message pipeline

**Изменить:**
- `src/core/bot.py` - добавить PII detection перед сохранением

**Код:**
```python
from src.nlp.pii_protector import PIIProtector

# В handle_message
pii_protector = PIIProtector()
await pii_protector.initialize()

# Проверить на PII
pii_entities = await pii_protector.detect_pii(message_text, language="ru")
if pii_entities:
    # Предупредить пользователя
    await update.message.reply_text(
        "Я заметил, что вы поделились личной информацией. "
        "Для вашей безопасности, пожалуйста, избегайте указывать "
        "имена, адреса, телефоны и другие личные данные."
    )

# Anonymize для хранения
safe_message = await pii_protector.anonymize_text(message_text, language="ru")
# Сохранить safe_message вместо оригинала
```

### Приоритет 4: Улучшение UX

**Задача:** Добавить кнопки и inline клавиатуры

**Примеры:**
```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# В handle_emotion_check - предложить техники
keyboard = [
    [InlineKeyboardButton("🧘 Дыхательные упражнения", callback_data="technique_breathing")],
    [InlineKeyboardButton("💭 Когнитивное переосмысление", callback_data="technique_cbt")],
    [InlineKeyboardButton("✍️ Написать письмо", callback_data="start_letter")],
]
reply_markup = InlineKeyboardMarkup(keyboard)
await update.message.reply_text("Чем я могу помочь?", reply_markup=reply_markup)
```

---

## 📚 Полезные ресурсы для Sprint 2

### Документация
- [LangGraph Tutorial](https://python.langchain.com/docs/langgraph)
- [python-telegram-bot Examples](https://docs.python-telegram-bot.org/en/stable/)
- [GoEmotions Dataset](https://github.com/google-research/google-research/tree/master/goemotions)
- [Presidio Documentation](https://microsoft.github.io/presidio/)

### Терапевтические техники
- CBT: "Feeling Good" by David Burns
- Grounding: "The Body Keeps the Score" by Bessel van der Kolk
- NVC: "Nonviolent Communication" by Marshall Rosenberg
- Parental Alienation: specialized resources в IP-планах

### Модели для загрузки
```bash
# GoEmotions Russian
# Проверить на HuggingFace: seara/rubert-base-go-emotions
# или monologg/bert-base-cased-goemotions-original

# Mental Health models
# mental/mental-bert-base-uncased
```

---

## 🐛 Debugging Tips

### Если бот не запускается:

1. **Import errors:**
   ```bash
   # Проверить установку
   pip list | grep telegram
   pip install -r requirements.txt --force-reinstall
   ```

2. **Database errors:**
   ```bash
   # Проверить подключение
   psql -U postgres -d pas_bot -c "SELECT 1"

   # Пересоздать БД
   dropdb pas_bot && createdb pas_bot
   alembic upgrade head
   ```

3. **Model loading errors:**
   ```bash
   # Проверить модели
   python -c "import spacy; print(spacy.load('ru_core_news_sm'))"

   # Переустановить
   python -m spacy download ru_core_news_sm --force
   ```

4. **Telegram API errors:**
   ```bash
   # Проверить токен
   curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe

   # Убедиться что токен в .env
   grep TELEGRAM .env
   ```

### Enable debug mode:

```bash
# В .env
LOG_LEVEL=DEBUG
DEBUG=True

# Запустить
python main.py

# Или через Makefile
make run-debug
```

---

## 🧪 Тестирование

### Сценарии для тестирования:

1. **Нормальный диалог:**
   - Отправить обычное сообщение
   - Проверить что бот отвечает
   - Эмоция должна определяться

2. **Кризисный сценарий:**
   ```
   User: "Я больше не могу, хочу покончить с этим"
   Bot: Должен предложить кризисную поддержку + номера помощи
   ```

3. **PII защита:**
   ```
   User: "Меня зовут Иван Петров, мой телефон +79991234567"
   Bot: Должен предупредить о PII
   ```

4. **Юридические вопросы:**
   ```
   User: "Могу ли я подать в суд?"
   Bot: Должен отказать и предложить консультацию юриста
   ```

### Автоматические тесты:

```bash
# Запустить все тесты
pytest

# С покрытием
pytest --cov=src

# Конкретный модуль
pytest tests/test_config.py -v
```

---

## 📊 Метрики для отслеживания

В процессе разработки отслеживайте:

### Technical Metrics:
- Response time (должно быть <2s)
- Memory usage
- Error rate
- API call count (OpenAI)

### Functional Metrics:
- Emotion detection accuracy
- Crisis detection recall (must be >95%)
- PII leakage (must be 0%)
- User engagement (messages per session)

### Логирование:
Все метрики уже логируются через structlog. Смотрите в:
```bash
tail -f data/logs/pas_bot.log | grep -E "emotion|crisis|pii"
```

---

## 🆘 Если что-то пошло не так

### Проблема: Бот не отвечает
- Проверить логи: `tail -f data/logs/*`
- Убедиться что бот запущен: `ps aux | grep python`
- Проверить Telegram webhook: может нужен polling mode

### Проблема: Models не загружаются
- Проверить интернет
- Попробовать загрузить вручную:
  ```python
  from transformers import AutoModel
  AutoModel.from_pretrained("model_name")
  ```
- Проверить места на диске (модели ~1-2GB)

### Проблема: Медленная работа
- Первый запуск всегда медленнее (загрузка моделей)
- Для production используйте GPU
- Включите кэширование моделей

### Нужна помощь?
1. Проверить логи в `data/logs/`
2. Запустить в debug mode: `make run-debug`
3. Проверить существующие issues в документации
4. Изучить ARCHITECTURE.md для понимания системы

---

## ✅ Checklist готовности к Sprint 2

Перед началом Sprint 2 убедитесь:

- [ ] Бот запускается без ошибок
- [ ] Все базовые команды работают
- [ ] База данных подключена
- [ ] Crisis detection реагирует
- [ ] Guardrails активны
- [ ] Логирование работает
- [ ] Документация прочитана
- [ ] .env настроен
- [ ] Тесты проходят

**Если все галочки стоят - вы готовы к Sprint 2!** 🎉

---

## 📅 Рекомендуемый план

### Неделя 1 Sprint 2:
- День 1-2: Emotion detection integration
- День 3-4: Basic techniques (CBT, grounding)
- День 5: PII protection activation

### Неделя 2 Sprint 2:
- День 1-2: UX improvements (кнопки, клавиатуры)
- День 3-4: Session management improvements
- День 5: Testing и документация

### Sprint 3 старт:
- RAG infrastructure setup
- Knowledge base preparation

---

**Удачи в разработке!** 🚀

Если нужна помощь на любом этапе - вся документация в `docs/` и комментарии в коде помогут разобраться.

**Let's build something meaningful together!** ❤️