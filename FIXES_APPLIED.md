# Исправления Применённые к PAS Bot

## Дата: 08.11.2025

## Проблемы и Решения

### 1. ❌ ПРОБЛЕМА: Бот НЕ помнит контекст диалога

**Симптом**: Бот говорит о "дочери", хотя пользователь упоминал "сына"

**Причина**:
- В `state_manager.py` (строка 686-691) context НЕ содержал `user_state`
- В `active_listening.py` ожидается `context.get("user_state")` для получения message_history
- История диалога НЕ передавалась в OpenAI API

**Исправление** (`state_manager.py:691`):
```python
# БЫЛО:
context = {
    "emotion": primary_emotion,
    "emotion_intensity": emotional_intensity,
    "language": "russian",
    "message_count": user_state.messages_count
}

# СТАЛО:
context = {
    "emotion": primary_emotion,
    "emotion_intensity": emotional_intensity,
    "language": "russian",
    "message_count": user_state.messages_count,
    "user_state": user_state  # CRITICAL: Pass user_state for message history
}
```

**Результат**: Теперь OpenAI получает последние 10 сообщений диалога через:
```python
# active_listening.py:187-193
if user_state and hasattr(user_state, 'message_history'):
    for msg in user_state.message_history[-10:]:
        if hasattr(msg, 'type'):
            if msg.type == 'human':
                messages.append({"role": "user", "content": msg.content})
            elif msg.type == 'ai':
                messages.append({"role": "assistant", "content": msg.content})
```

---

### 2. ❌ ПРОБЛЕМА: Команды /letter и /goals не работают

**Симптом**:
- При вводе `/letter` бот просто задаёт вопросы вместо начала процесса написания письма
- Команда игнорируется как обычный текст

**Причина**:
- Команды `/letter` и `/goals` были в меню (строки 308-309)
- НО обработчики (CommandHandler) НЕ были зарегистрированы
- Telegram отправлял команды как обычный текст

**Исправление 1** - Добавлены обработчики команд (`bot.py:89-117`):
```python
async def letter_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /letter command - start letter writing."""
    user_id = str(update.effective_user.id)

    log_user_interaction(logger, user_id=user_id, message_type="command", command="letter")

    # Process through state manager with "письмо" keyword
    response = await self.state_manager.process_message(user_id, "хочу написать письмо")
    await update.message.reply_text(response)

async def goals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /goals command - view goals."""
    user_id = str(update.effective_user.id)

    log_user_interaction(logger, user_id=user_id, message_type="command", command="goals")

    # Process through state manager with "цель" keyword
    response = await self.state_manager.process_message(user_id, "покажи мои цели")
    await update.message.reply_text(response)
```

**Исправление 2** - Зарегистрированы обработчики (`bot.py:321-322`):
```python
# БЫЛО:
app.add_handler(CommandHandler("start", self.start_command))
app.add_handler(CommandHandler("help", self.help_command))
app.add_handler(CommandHandler("crisis", self.crisis_command))
app.add_handler(CommandHandler("privacy", self.privacy_command))

# СТАЛО:
app.add_handler(CommandHandler("start", self.start_command))
app.add_handler(CommandHandler("help", self.help_command))
app.add_handler(CommandHandler("letter", self.letter_command))  # НОВОЕ
app.add_handler(CommandHandler("goals", self.goals_command))    # НОВОЕ
app.add_handler(CommandHandler("crisis", self.crisis_command))
app.add_handler(CommandHandler("privacy", self.privacy_command))
```

**Результат**:
- `/letter` → запускает процесс написания письма
- `/goals` → показывает цели пользователя

---

## Архитектура Работы Бота

### Поток Обработки Сообщений

```
Telegram Message
    ↓
bot.py (handle_message)
    ↓
PII Detection (отключено)
    ↓
Crisis Detection (keyword-based)
    ↓
StateManager.process_message()
    ↓
    ├─ Сохранение в user_state.message_history (HumanMessage)
    ├─ Увеличение messages_count
    ↓
State Graph (LangGraph)
    ↓
    ├─→ emotion_check (keyword-based)
    ├─→ route по дистрессу:
    │   ├─→ high → crisis_support
    │   ├─→ moderate → moderate_support
    │   └─→ low → casual_chat
    ↓
technique_selection
    ↓
    ├─ Создание context с user_state (ТЕПЕРЬ!)
    ├─ TechniqueOrchestrator.select_and_apply_technique()
    ↓
Active Listening
    ↓
    ├─ Извлечение message_history из context["user_state"]
    ├─ Построение messages для OpenAI (system + последние 10 сообщений)
    ├─ Определение stage (1-2: слушание, 3-5: понимание, 6+: действия)
    ↓
OpenAI API (gpt-4-turbo-preview)
    ↓
    ├─ temperature=0.8
    ├─ presence_penalty=0.6
    ├─ frequency_penalty=0.6
    ↓
Supervisor Agent (качество ответа)
    ↓
Response → Telegram
```

### Память Диалога

**В памяти (UserState)**:
```python
class UserState:
    user_id: str
    message_history: List[Message]  # LangChain HumanMessage/AIMessage
    messages_count: int             # Счётчик для определения стадии
    current_state: ConversationState
    completed_techniques: List[str]
    goals: List[Goal]
```

**Передача в OpenAI**:
```python
# active_listening.py:184-196
messages = [{"role": "system", "content": system_prompt}]

# Последние 10 сообщений из истории
for msg in user_state.message_history[-10:]:
    if msg.type == 'human':
        messages.append({"role": "user", "content": msg.content})
    elif msg.type == 'ai':
        messages.append({"role": "assistant", "content": msg.content})

# Текущее сообщение
messages.append({"role": "user", "content": user_message})
```

### Прогрессия Диалога (Stage-Based)

**Этапы** (`active_listening.py:133-138`):
```python
if message_count <= 2:
    stage = "начало диалога - активное слушание и валидация"
elif message_count <= 5:
    stage = "понимание ситуации - сбор деталей"
else:
    stage = "переход к действиям - предложите письмо или упражнение"
```

**System Prompt** (`active_listening.py:141-180`):
- **Сообщения 1-2**: Активное слушание, валидация, БЕЗ шаблонов
- **Сообщения 3-5**: Глубокое понимание, уточнение деталей
- **Сообщения 6+**: Мягкий переход к действиям (письма, упражнения)

**Принципы**:
- ✓ Говорите как живой человек, НЕ как робот
- ✓ Варьируйте начало ответов
- ✓ БЕЗ шаблонов вроде "я здесь чтобы..."
- ✓ НЕ давайте юридических советов
- ✓ НЕ осуждайте другого родителя

---

## Что НЕ Сохраняется (TODO)

### ⚠️ База Данных

**Сейчас**:
- ✅ Метаданные пользователя (ID, timestamps)
- ✅ Эмоциональное состояние (emotional_score, crisis_level)
- ✅ Статистика (total_messages, total_sessions)
- ❌ История сообщений НЕ сохраняется в БД

**Проблема**:
- При перезапуске бота вся история message_history теряется
- Невозможна долгосрочная терапия

**Решение** (будущее):
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    role VARCHAR(20),  -- 'user' или 'assistant'
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    technique_used VARCHAR(50),
    emotion VARCHAR(50),
    metadata JSON
);
```

---

## Тестирование

### Как Проверить Память:

1. **Начните диалог с упоминанием конкретной детали**:
   ```
   "3 года не видел сына Максима"
   ```

2. **Продолжите диалог**:
   ```
   "Что мне делать?"
   ```

3. **Проверьте, что бот помнит**:
   - Бот должен упомянуть "сына" (НЕ "дочь")
   - Бот должен помнить имя "Максим"
   - Бот должен помнить "3 года"

### Как Проверить Прогрессию:

1. **Сообщения 1-2**: Бот слушает, задаёт уточняющие вопросы
2. **Сообщения 3-5**: Бот суммирует ситуацию, собирает детали
3. **Сообщения 6+**: Бот предлагает:
   - "Возможно, имеет смысл написать письмо?"
   - "Хотите попробовать упражнение?"

### Команды:

- `/start` - Перезапуск диалога
- `/letter` - Начать написание письма
- `/goals` - Посмотреть цели
- `/help` - Список команд

---

## Технические Детали

### Файлы Изменены:

1. **src/orchestration/state_manager.py** (строка 691):
   - Добавлен `user_state` в context

2. **src/core/bot.py** (строки 89-117, 321-322):
   - Добавлены обработчики `/letter` и `/goals`
   - Зарегистрированы CommandHandler

### Модель OpenAI:

```python
response = await client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=messages,  # С полной историей
    max_tokens=400,
    temperature=0.8,      # Вариативность
    presence_penalty=0.6, # Против повторов
    frequency_penalty=0.6 # Против повторов
)
```

---

## Следующие Шаги (Приоритеты)

### 🔥 Высокий Приоритет:
1. ✅ **DONE**: Передача истории в LLM
2. ✅ **DONE**: Улучшение system prompt с этапами
3. ✅ **DONE**: Регистрация команд /letter и /goals
4. ⏳ **TODO**: Тестирование новой реализации
5. ⏳ **TODO**: Создать таблицу messages и сохранять историю

### 🟡 Средний Приоритет:
6. Создать технику "Transition to Action" для явного предложения действий
7. Улучшить routing с учётом прогресса
8. Добавить dialogue_stage в users table

### 🟢 Низкий Приоритет:
9. Метрики прогресса пользователя
10. Персонализация промптов
11. A/B тестирование разных стилей

---

## Для Отладки

### Логи для Проверки:

```bash
# Фильтр по ключевым событиям
grep -E "(llm_response_generated|message_count|stage|process_message)" bot.log

# Проверка передачи истории
grep "message_history" bot.log

# Проверка обработки команд
grep "command.*letter" bot.log
```

### Проверка user_state:

```python
# В active_listening.py добавлен лог:
logger.info("llm_response_generated",
           message_length=len(response_text),
           message_count=message_count,
           stage=stage)
```
