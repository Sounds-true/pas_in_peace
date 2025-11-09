# Implementation Plan: QuestBuilderAssistant Conversational AI

## Смысл и цель задачи

Создать conversational AI assistant который помогает родителю создать персонализированный образовательный квест для ребенка через естественный диалог. Assistant собирает информацию о ребенке, семейных воспоминаниях, образовательных потребностях и генерирует YAML квеста с помощью GPT-4. Включает автоматическую модерацию контента на каждом шаге и reveal mechanics (ребенок постепенно догадывается кто создал квест).

## Архитектура решения

### Структура в pas_in_peace

```
src/techniques/
├── quest_builder.py              # Новый - основной файл
└── base.py                       # Существующий - базовый класс

src/safety/
└── content_moderator.py          # Новый - модерация контента

src/storage/
└── models.py                     # Расширить - Quest, QuestNode models

src/api/
└── websocket.py                  # Новый - WebSocket endpoints
```

### Ключевые компоненты

**QuestBuilderAssistant** - наследует от Technique
- Multi-stage state machine (INITIAL -> GATHERING -> GENERATING -> REVIEWING -> FINALIZING)
- Context management для сохранения прогресса
- Integration с ContentModerator на каждом этапе
- YAML generation через GPT-4

**ContentModerator** - проверка токсичности
- Pattern-based quick check (красные флаги)
- AI-based moderation через SupervisorAgent
- Quest-level validation перед export

**QuestContext** - состояние создания квеста
- Собранная информация (child_name, age, interests, memories)
- Текущая стадия
- Промежуточный YAML
- Moderation results

## Полный flow работы функционала

### Создание квеста - step by step

1. **Инициализация**
   - User нажимает "Create Quest" в веб-интерфейсе
   - Frontend открывает WebSocket connection к `/ws/quest-builder`
   - Backend создает QuestContext в памяти
   - AI отправляет welcome message с объяснением процесса

2. **Stage 1: INITIAL - Приветствие**
   - AI: "Давайте создадим квест для вашего ребенка! Расскажите о нем"
   - Parent: текстовый ответ
   - Переход к GATHERING

3. **Stage 2: GATHERING - Сбор информации**
   - AI последовательно спрашивает:
     - Имя и возраст ребенка
     - Что ребенок любит (динозавры, космос, футбол)
     - Любимые совместные воспоминания (поездки, традиции)
     - С какими предметами нужна помощь (математика, русский)
     - Какие манипуляции использует другой родитель (для защиты)
   - На каждом ответе: ContentModerator проверяет токсичность
   - Если токсично: просьба перефразировать + объяснение почему
   - Данные сохраняются в QuestContext

4. **Stage 3: GENERATING - AI генерация**
   - AI собирает все данные в prompt для GPT-4
   - GPT-4 генерирует структуру квеста в YAML формате
   - Квест включает:
     - Нейтральные образовательные узлы (30%)
     - Узлы с намеками на семью (40%)
     - Детективные узлы (20%)
     - Reveal узел (10%)
   - ContentModerator проверяет весь YAML
   - Переход к REVIEWING

5. **Stage 4: REVIEWING - Просмотр родителем**
   - AI показывает preview квеста (краткое описание узлов)
   - Parent может:
     - Принять квест
     - Попросить изменить конкретный узел
     - Попросить regenerate полностью
   - Если изменения: возврат к GENERATING
   - Если OK: переход к MODERATING

6. **Stage 5: MODERATING - Финальная модерация**
   - ContentModerator делает финальную проверку
   - Если токсичный контент найден:
     - Показать проблемные узлы
     - Предложить автоматические исправления
     - Дать возможность редактировать вручную
   - Если OK: переход к FINALIZING

7. **Stage 6: FINALIZING - Экспорт**
   - AI спрашивает: добавить контакт другого родителя для notifications?
   - Quest сохраняется в database
   - YAML экспортируется для inner_edu
   - Parent получает link на квест
   - Track "Child Connection" обновляется (+30% прогресс)

## API и интерфейсы

### QuestBuilderAssistant

**Основные методы**
- `execute(message, context)` - обработать сообщение от родителя
- `_handle_initial(message, context, quest_ctx)` - stage INITIAL
- `_handle_gathering(message, context, quest_ctx)` - stage GATHERING
- `_handle_generating(message, context, quest_ctx)` - stage GENERATING
- `_handle_reviewing(message, context, quest_ctx)` - stage REVIEWING
- `_handle_moderating(message, context, quest_ctx)` - stage MODERATING
- `_handle_finalizing(message, context, quest_ctx)` - stage FINALIZING
- `_generate_quest_with_ai(quest_data)` - вызов GPT-4
- `_export_to_yaml(quest_structure)` - конвертация в YAML
- `_save_to_database(quest_yaml, metadata)` - сохранение
- `_send_to_inner_edu(quest_id, yaml)` - экспорт в inner_edu

### ContentModerator

**Методы модерации**
- `check_content(text, context_type)` - проверка одного сообщения
- `moderate_quest(quest_yaml)` - проверка всего квеста
- `get_toxic_patterns()` - получить список красных флагов
- `suggest_fixes(toxic_content)` - предложить исправления

**Возвращаемые данные**
- `ModerationResult`:
  - approved (bool)
  - is_toxic (bool)
  - toxic_phrases (list)
  - problematic_nodes (list для квеста)
  - suggested_fixes (dict)

### WebSocket Protocol

**Messages от client**
```
{
  "type": "message",
  "content": "user message text",
  "quest_id": "optional if continuing"
}
```

**Messages от server**
```
{
  "type": "ai_response",
  "content": "AI message",
  "stage": "current_stage",
  "moderation": {
    "status": "ok|warning|blocked",
    "message": "optional warning"
  }
}
```

## Взаимодействие компонентов

```
Frontend (WebSocket client)
  |
  v
WebSocket Endpoint (/ws/quest-builder)
  |
  v
StateManager.handle_message()
  |
  v
QuestBuilderAssistant.execute(message, context)
  |
  +---> Get/Create QuestContext from context["quest_contexts"]
  |
  +---> Determine current stage
  |
  +---> Call stage-specific handler
        |
        +---> ContentModerator.check_content(message)
        |       |
        |       +---> Quick pattern check
        |       +---> AI moderation (SupervisorAgent)
        |       +---> Return ModerationResult
        |
        +---> If stage == GENERATING:
        |       |
        |       +---> _generate_quest_with_ai()
        |               |
        |               +---> Build GPT-4 prompt
        |               +---> Call OpenAI API
        |               +---> Parse YAML response
        |               +---> ContentModerator.moderate_quest()
        |               +---> Return quest_yaml
        |
        +---> If stage == FINALIZING:
                |
                +---> _save_to_database(quest_yaml)
                +---> _send_to_inner_edu(quest_id, yaml)
                +---> Update RecoveryTrack progress
                +---> Return completion message
```

## Порядок реализации

### Step 1: Base Infrastructure (дни 1-2)

1. Создать QuestContext dataclass
2. Создать QuestStage enum
3. Создать skeleton QuestBuilderAssistant класса
4. Добавить в StateManager.techniques registry

### Step 2: Content Moderation (дни 3-4)

1. Создать ContentModerator класс
2. Добавить toxic patterns (regex)
3. Integration с SupervisorAgent
4. Quest-level moderation logic
5. Unit tests для модерации

### Step 3: Stage Handlers (дни 5-8)

1. Implement _handle_initial()
2. Implement _handle_gathering() с sub-questions flow
3. Implement _handle_reviewing()
4. Implement _handle_moderating()
5. Implement _handle_finalizing()

### Step 4: AI Generation (дни 9-11)

1. Создать GPT-4 prompt template для квестов
2. Implement _generate_quest_with_ai()
3. YAML parsing и validation
4. Reveal mechanics generation (progressive hints)
5. Retry logic если GPT-4 генерирует невалидный YAML

### Step 5: Database Integration (день 12)

1. Extend Quest model в models.py
2. Implement _save_to_database()
3. Implement _send_to_inner_edu() API call
4. Migration для новых полей

### Step 6: WebSocket Endpoint (дни 13-14)

1. Создать WebSocket endpoint в FastAPI
2. Connection management
3. Message routing к QuestBuilderAssistant
4. Error handling
5. Connection timeout handling

### Step 7: Testing & Polish (дни 15-17)

1. End-to-end test создания квеста
2. Test moderation edge cases
3. Test AI generation failures
4. Performance testing (concurrent users)
5. Logging improvements

## Критичные граничные случаи

**GPT-4 генерирует невалидный YAML**
- Parse error handling
- Retry с более explicit prompt
- Fallback на template-based generation после 3 retries

**Moderation блокирует весь квест**
- Показать конкретные проблемные узлы
- Дать возможность редактировать каждый узел
- Предложить AI suggestions для исправления

**WebSocket connection drops mid-conversation**
- Auto-save QuestContext каждые 30 секунд
- Resume from last saved state при reconnect
- Показать "Connection lost" warning

**User отправляет PII (phone, email)**
- PII protector detect перед moderation
- Warn user не включать personal info
- Автоматически mask в saved data

## Объем работ

### Входит в реализацию

- QuestBuilderAssistant с 6 stages
- ContentModerator для safety
- GPT-4 integration для generation
- YAML export в inner_edu формат
- WebSocket endpoint
- Database models для Quest
- Reveal mechanics в квесте (progressive hints)
- Auto-save progress
- Error handling и retry logic

### Не входит в MVP

- Visual quest editor (только conversational)
- Template library (pre-made квесты)
- Collaborative editing (multiple parents)
- Version history для квестов
- A/B testing разных промптов
- Advanced AI (fine-tuned модель)
- Multi-language quests

## Допущения

- OpenAI API доступен и квота достаточна
- GPT-4 может генерировать валидный YAML (с правильным промптом)
- SupervisorAgent уже реализован в pas_in_peace
- Inner_edu API принимает YAML формат
- WebSocket поддерживается в deployment среде
- Quest YAML schema определен в inner_edu

## Открытые вопросы

1. Какой максимальный размер квеста в узлах (50? 100?)?
2. Как часто можно regenerate квест (rate limiting)?
3. Нужна ли возможность pause и resume через несколько дней?
4. Что делать если OpenAI API unavailable во время generation?
5. Как версионировать квесты при редактировании?

## Acceptance Criteria

- Родитель может создать квест через conversational dialogue
- AI задает все необходимые вопросы (child info, interests, memories)
- Moderation блокирует токсичный контент (>95% accuracy на тестовых данных)
- GPT-4 генерирует валидный YAML квест (>90% success rate)
- Квест включает reveal mechanics (намеки -> раскрытие)
- WebSocket connection stable (auto-reconnect работает)
- Quest сохраняется в database
- YAML экспортируется для inner_edu
- RecoveryTrack progress обновляется
- Весь процесс занимает 10-15 минут

## Definition of Done

- Все stage handlers реализованы
- ContentModerator протестирован на toxic samples
- GPT-4 prompts отлажены (генерируют валидный YAML)
- WebSocket endpoint работает
- Database migrations applied
- Logging всех stages и errors
- Error handling для всех API calls
- Documentation для GPT-4 prompts
- Metrics для quest_creation_duration, moderation_failures

## Минимальные NFR для MVP

**Производительность**
- AI response time: <2s для обычных сообщений
- GPT-4 generation: <30s для полного квеста
- Moderation check: <1s
- WebSocket latency: <500ms

**Надежность**
- Auto-save каждые 30 секунд
- Retry GPT-4 calls до 3 раз
- Graceful degradation если OpenAI unavailable
- WebSocket reconnect автоматически

**Ресурсы**
- OpenAI API cost: <$0.50 per quest
- Concurrent quest creations: до 50
- Max quest size: 100 nodes

## Требования безопасности

- Content moderation на КАЖДОМ user input
- PII detection перед сохранением
- YAML sanitization (prevent code injection)
- Rate limiting: 5 quest creations per hour per user
- OpenAI API key только через environment variable
- Quest content encrypted at rest (опционально для MVP)

## Наблюдаемость

**Логи**
- quest_creation_started (quest_id, user_id)
- quest_stage_changed (quest_id, from_stage, to_stage)
- moderation_check (quest_id, result)
- gpt4_generation_called (quest_id, prompt_tokens)
- quest_created (quest_id, nodes_count, generation_time)

**Метрики**
- quests_created_total (counter)
- quest_creation_duration_seconds (histogram)
- moderation_failures_total (counter)
- gpt4_api_errors_total (counter)
- websocket_connections_active (gauge)

**Alerts**
- OpenAI API error rate >10%
- Moderation block rate >50%
- Average generation time >60s

## Релиз

**Feature Flag**
- `quest_builder_enabled` - enable/disable quest creation
- `strict_moderation` - toggle strict/relaxed moderation

**Rollout**
1. Alpha: 5 internal testers
2. Beta: 50 selected users
3. GA: gradual 10% -> 50% -> 100%

## Откат

**Условия отката**
- >30% moderation false positives
- OpenAI costs exceed budget ($100/day)
- >20% YAML generation failures
- WebSocket instability (>50% disconnects)

**Шаги отката**
1. Disable feature flag `quest_builder_enabled`
2. Show "Coming soon" message в UI
3. Preserve existing quests (no deletion)

## Риски и митигации

- **Риск 1**: GPT-4 генерирует inappropriate content - Митигация: strict prompts, double moderation
- **Риск 2**: OpenAI API rate limits - Митигация: queue system, exponential backoff
- **Риск 3**: Toxic content проходит модерацию - Митигация: manual review queue, user reporting
- **Риск 4**: YAML schema mismatch с inner_edu - Митигация: shared schema validation, version control
- **Риск 5**: WebSocket scaling issues - Митигация: connection pooling, horizontal scaling

## Параметры стека

**Языки**
- Python 3.11+

**Фреймворки**
- FastAPI (WebSocket support)
- LangChain (для GPT-4 integration)
- Pydantic (data validation)

**AI/ML**
- OpenAI GPT-4 API
- SupervisorAgent (existing)

**Database**
- PostgreSQL 15
- SQLAlchemy 2.0

**Deployment**
- WebSocket support required
- Redis для WebSocket state (опционально)

## Самопроверка плана перед выдачей

- ✅ Нет кода (только описание)
- ✅ Все секции заполнены
- ✅ Realistic timeline (17 дней)
- ✅ Учтена модерация контента
- ✅ Описана интеграция с существующими компонентами
