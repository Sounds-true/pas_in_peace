# Implementation Plan: Multi-Track Recovery System

## Смысл и цель задачи

Создать систему параллельных recovery треков которая дает родителю ясное понимание "куда мы идем" и прогресс по каждому направлению. 4 трека работают одновременно (Self Work, Child Connection, Negotiation, Community Support) с визуализацией прогресса, milestones и AI-рекомендациями следующих шагов. Интеграция с существующей StateManager для seamless UX.

## Архитектура решения

### Структура компонентов

**Backend Integration (pas_in_peace)**

```
src/orchestration/
├── state_manager.py              # Существующий - расширить
├── multi_track.py                # Новый - core logic
└── track_transitions.py          # Новый - переходы между треками

src/storage/
└── models.py                     # Расширить User model

src/api/
└── web_endpoints.py              # Добавить /tracks endpoints
```

### Ключевые концепции

**RecoveryTrack** - один из 4 параллельных путей:
- SELF_WORK - эмоциональная проработка, CBT, письма себе
- CHILD_CONNECTION - квесты, письма ребенку, фотоальбомы
- NEGOTIATION - переговоры с алиенатором, юридические действия
- COMMUNITY - поиск групп поддержки, общение с другими родителями

**TrackProgress** - состояние одного трека:
- current_phase (enum): AWARENESS → EXPRESSION → ACTION → MASTERY
- completion_percentage (0-100)
- milestones_achieved (list)
- next_suggested_action (AI-generated)
- last_activity_date

**Primary Track** - текущий фокус пользователя (можно менять)

**Cross-Track Actions** - некоторые действия прогрессируют несколько треков (например, квест = SELF_WORK + CHILD_CONNECTION)

## Полный flow работы функционала

### Scenario 1: Новый пользователь начинает journey

1. User отправляет первое сообщение в Telegram бота
2. StateManager инициализирует UserState
3. MultiTrackManager создает 4 пустых трека в User.recovery_tracks (JSON)
4. Bot отправляет welcome message с объяснением системы треков
5. AI Assistant спрашивает: "Что сейчас для вас важнее всего?"
6. User выбирает primary track (например, SELF_WORK)
7. Bot показывает текущий plan для этого трека:
   - Phase 1: Understanding your emotions (0% → 25%)
   - Next action: "Let's start with an emotional check-in"
8. User проходит emotional check-in
9. Progress обновляется: SELF_WORK 0% → 10%
10. Bot: "Great! You completed your first milestone in Self Work track"

### Scenario 2: Переключение между треками

1. User в середине SELF_WORK трека (50% прогресс)
2. User отправляет "/progress" команду
3. Bot показывает dashboard всех 4 треков:
   ```
   🧠 Self Work: ████████░░ 80%
      Next: Write a letter to yourself

   👨‍👦 Child Connection: ███░░░░░░░ 30%
      Next: Create a quest for your child

   🤝 Negotiation: █░░░░░░░░░ 10%
      Next: Review your court documents

   🌍 Community: ██░░░░░░░░ 20%
      Next: Find a support group
   ```
4. User: "Я хочу создать квест для ребенка"
5. Bot распознает это как CHILD_CONNECTION action
6. StateManager автоматически переключает context на этот трек
7. QuestBuilderAssistant запускается
8. После создания квеста обновляются ОБА трека:
   - CHILD_CONNECTION: 30% → 60% (major milestone)
   - SELF_WORK: 80% → 85% (creative expression)

### Scenario 3: AI-рекомендации следующего действия

1. User завершил emotional check-in (SELF_WORK)
2. MultiTrackManager анализирует:
   - User context (emotional state, therapy phase)
   - Current progress по всем трекам
   - Time since last activity в каждом треке
   - User's stated goals
3. AI генерирует персонализированные рекомендации:
   - "You've made great progress in Self Work! Ready to reconnect with your child? Try creating a quest (Child Connection track)"
   - "It's been 2 weeks since you worked on Negotiation. Consider reviewing your strategy."
4. User может:
   - Принять suggestion (bot направляет в нужный трек)
   - Отклонить и продолжить текущий трек
   - Попросить показать все варианты

## API и интерфейсы

### MultiTrackManager Class

**Основные методы**

- `initialize_tracks(user_id)` - создать 4 пустых трека для нового пользователя
- `get_all_progress(user_id)` - получить состояние всех треков
- `get_primary_track(user_id)` - какой трек сейчас в фокусе
- `set_primary_track(user_id, track)` - сменить фокус
- `update_progress(user_id, track, delta, action_type)` - обновить прогресс
- `check_milestone(user_id, track)` - проверить достигнут ли milestone
- `get_next_action(user_id, track)` - AI recommendation для трека
- `get_cross_track_impact(action_type)` - какие треки прогрессируют от действия

**Внутренняя структура**

RecoveryTrack (Enum):
```python
SELF_WORK = "self_work"
CHILD_CONNECTION = "child_connection"
NEGOTIATION = "negotiation"
COMMUNITY = "community"
```

TrackPhase (Enum):
```python
AWARENESS = "awareness"      # 0-25%
EXPRESSION = "expression"    # 25-50%
ACTION = "action"           # 50-75%
MASTERY = "mastery"         # 75-100%
```

TrackProgress (TypedDict):
```python
{
  "track": RecoveryTrack,
  "phase": TrackPhase,
  "completion_percentage": int,  # 0-100
  "milestones": [
    {"name": str, "achieved_at": datetime, "description": str}
  ],
  "next_action": {
    "suggestion": str,
    "technique": str,  # какую Technique запустить
    "estimated_time": str
  },
  "last_activity": datetime,
  "total_actions": int
}
```

### StateManager Integration

**Расширения существующего класса**

Добавить в UserState:
```python
recovery_tracks: Dict[RecoveryTrack, TrackProgress]
primary_track: RecoveryTrack
track_switch_count: int
```

Новые методы в StateManager:
- `get_current_track_context()` - какой трек активен сейчас
- `should_suggest_track_switch()` - надо ли предложить переключиться
- `handle_track_aware_message(message)` - routing с учетом треков

**Routing Logic**

При обработке сообщения:
1. Detect intent (CBT, letter, quest, resource search)
2. Map intent → RecoveryTrack
3. Check if switch needed (primary_track ≠ detected_track)
4. If switch: ask confirmation или auto-switch (зависит от confidence)
5. Route to appropriate Technique
6. После выполнения: update progress для всех affected треков

### Database Schema

**User Model Extensions**

Добавить поля:
```python
recovery_tracks = Column(JSON, default={})  # Dict[str, TrackProgress]
primary_track = Column(String, default="self_work")
recovery_week = Column(Integer, default=0)  # неделя с начала journey
recovery_day = Column(Integer, default=0)   # день в текущей неделе
```

**TrackMilestone Model** (новая таблица)

```python
class TrackMilestone(Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    track = Column(String)  # RecoveryTrack enum
    milestone_type = Column(String)  # "first_letter", "quest_created", etc.
    achieved_at = Column(DateTime)
    metadata = Column(JSON)  # дополнительные данные
```

### Web API Endpoints

**GET /api/tracks/progress**
- Authorization: JWT required
- Response:
```json
{
  "primary_track": "self_work",
  "tracks": {
    "self_work": {
      "phase": "expression",
      "completion_percentage": 65,
      "milestones": [...],
      "next_action": {...}
    },
    "child_connection": {...},
    "negotiation": {...},
    "community": {...}
  },
  "overall_progress": 45,
  "journey_start_date": "2025-01-15",
  "days_active": 23
}
```

**POST /api/tracks/set-primary**
- Body: `{"track": "child_connection"}`
- Response: updated progress

**GET /api/tracks/suggestions**
- Response: AI-generated next actions для всех треков

## Взаимодействие компонентов

```
User Message (Telegram or Web)
  |
  v
StateManager.handle_message()
  |
  +---> MultiTrackManager.detect_intent(message)
  |       |
  |       +---> Intent: "create quest" → CHILD_CONNECTION
  |       +---> Intent: "CBT exercise" → SELF_WORK
  |       +---> Intent: "find lawyer" → NEGOTIATION
  |
  +---> Check if primary_track == detected_track
  |       |
  |       +---> If NO: suggest switch or auto-switch
  |       +---> If YES: continue
  |
  +---> Route to Technique (QuestBuilder, CBT, LetterWriting, etc.)
  |
  +---> Technique.execute()
  |       |
  |       +---> Action completed
  |
  +---> MultiTrackManager.update_progress()
        |
        +---> Calculate progress delta
        +---> Check for cross-track impact
        +---> Update multiple tracks if needed
        +---> Check if milestone achieved
        +---> Generate next action suggestion
        |
        v
    DatabaseManager.update_user_tracks()
        |
        v
    Response to user with progress update
```

## Порядок реализации

### Step 1: Data Models (дни 1-2)

1. Создать enums (RecoveryTrack, TrackPhase)
2. Создать TypedDict для TrackProgress
3. Extend User model с recovery_tracks, primary_track
4. Create TrackMilestone model
5. Alembic migration

### Step 2: MultiTrackManager Core (дни 3-5)

1. Implement initialize_tracks()
2. Implement get_all_progress()
3. Implement update_progress() с milestone checking
4. Implement cross-track impact logic
5. Unit tests для всех методов

### Step 3: StateManager Integration (дни 6-8)

1. Add track detection logic (intent → track mapping)
2. Implement track switching logic
3. Update existing Techniques to report track impact
4. Add track context to conversation state
5. Integration tests

### Step 4: AI Suggestions (дни 9-10)

1. Implement get_next_action() с GPT-4 integration
2. Create prompt templates для suggestions
3. Context-aware recommendations (учитывать emotional state)
4. Test suggestions quality

### Step 5: Telegram Commands (день 11)

1. Implement /progress command
2. Implement /switch_track command
3. Визуализация прогресса в Telegram (progress bars)
4. Inline keyboards для выбора трека

### Step 6: Web API (день 12)

1. Create /api/tracks/* endpoints
2. Integration с frontend (MultiTrackProgress component)
3. WebSocket updates для real-time progress

### Step 7: Milestones & Gamification (дни 13-14)

1. Define milestone criteria для каждого трека
2. Achievement notifications
3. Celebration messages при достижении milestones
4. Track completion rewards

### Step 8: Testing & Polish (дни 15-17)

1. End-to-end tests всех треков
2. Test track switching scenarios
3. Test cross-track impact
4. Performance testing (progress calculations)
5. Documentation

## Критичные граничные случаи

**User застрял на одном треке**
- Если progress по треку >30 дней не менялся
- AI suggests switching: "You've been focused on Self Work. Ready to reconnect with your child?"
- Gentle nudge без pressure

**Conflicting track priorities**
- User хочет и квест создать (CHILD_CONNECTION) и CBT (SELF_WORK)
- Показать что квест ВКЛЮЧАЕТ элементы self work
- Объяснить cross-track benefits

**Progress regression**
- Если user удаляет проект (квест/письмо)
- НЕ уменьшать progress (recovery не linear)
- Milestone остается achieved
- Только next_action обновляется

**Milestone не достигается долго**
- Если застрял на 45% в течение недель
- AI предлагает easier next action
- Или suggests switching track для motivation boost

## Объем работ

### Входит в реализацию

- MultiTrackManager класс (~500 lines)
- RecoveryTrack и TrackPhase enums
- TrackProgress TypedDict
- User model extensions
- TrackMilestone model
- Alembic migration
- StateManager integration (~200 lines)
- Intent detection (message → track mapping)
- Track switching logic
- Cross-track impact calculations
- Milestone checking
- AI next action suggestions (GPT-4)
- /progress Telegram command
- /api/tracks/* endpoints (4 endpoints)
- Unit tests (~300 lines)
- Integration tests

### Не входит в MVP

- Machine learning для track recommendations
- Predictive analytics (когда user достигнет цели)
- Social features (сравнение прогресса с другими)
- Track customization (user defines own tracks)
- Advanced gamification (badges, leaderboards)
- Track history visualization (graphs по времени)

## Допущения

- Existing StateManager architecture compatible с track system
- UserState уже имеет все нужные fields (therapy_phase, emotional_score)
- DatabaseManager поддерживает JSON columns
- OpenAI API доступен для next action suggestions
- Frontend (MultiTrackProgress component) будет создан отдельно (IP-02)

## Открытые вопросы

1. Как часто пересчитывать AI suggestions - каждый раз или cache?
2. Нужна ли возможность pause track (временно выключить)?
3. Как показывать "overall recovery progress" - среднее или weighted?
4. Должен ли bot автоматически переключать primary_track или всегда спрашивать?
5. Как обрабатывать ситуацию "хочу работать над всеми треками одновременно"?

## Acceptance Criteria

- Новый user видит explanation системы треков при onboarding
- Все 4 трека инициализируются со значениями по умолчанию
- User может выбрать primary track
- Каждое действие обновляет progress соответствующих треков
- Milestones автоматически достигаются при прохождении thresholds
- /progress команда показывает все треки с прогрессом
- AI генерирует релевантные next action suggestions
- Cross-track actions (квест) обновляют несколько треков
- Track switching работает seamlessly без потери контекста
- Web dashboard показывает real-time progress

## Definition of Done

- MultiTrackManager реализован и протестирован
- User model migration applied
- StateManager integration работает
- Intent detection достигает >85% accuracy
- AI suggestions релевантны (manual review на тестовых данных)
- /progress command работает в Telegram
- API endpoints задокументированы
- Unit test coverage >80%
- Integration tests для всех track switching scenarios
- Logging всех track updates
- Metrics для track_progress_updated, milestone_achieved

## Минимальные NFR для MVP

**Производительность**
- Progress calculation: <50ms
- AI next action generation: <3s
- /progress command response: <1s
- Track switch latency: <100ms

**Надежность**
- Progress никогда не уменьшается (только вперед)
- Milestone достижения persistent (не теряются при bugs)
- Graceful degradation если AI suggestions unavailable

**Capacity**
- До 10000 users tracking progress одновременно
- До 100 milestones per user
- 4 трека per user (fixed для MVP)

## Требования безопасности

- Track data хранится в user's record (изоляция)
- NO sharing track progress с другими users (privacy)
- Milestone data NO PII (только metadata)
- Rate limiting на AI suggestions (prevent abuse)
- Input validation на track names (enum only)

## Наблюдаемость

**Логи**
- track_initialized (user_id, all_tracks)
- track_switched (user_id, from_track, to_track)
- progress_updated (user_id, track, old_%, new_%)
- milestone_achieved (user_id, track, milestone_name)
- next_action_suggested (user_id, track, suggestion)

**Метрики**
- track_progress_updates_total (counter, labeled by track)
- milestones_achieved_total (counter, labeled by milestone_type)
- primary_track_switches_total (counter)
- ai_suggestions_generated_total (counter)
- average_track_completion_percentage (gauge per track)

**Alerts**
- Users stuck (no progress >30 days)
- AI suggestion generation failing (>10% error rate)
- Unusual progress patterns (suspicious activity)

## Релиз

**Feature Flags**
- `multi_track_system_enabled` - enable/disable track system
- `ai_suggestions_enabled` - enable AI next actions
- `strict_milestones` - strict/relaxed milestone criteria

**Rollout Plan**
1. Alpha: 10 users testing all tracks
2. Beta: 100 users с feedback collection
3. GA: gradual 20% → 50% → 100%

## Откат

**Условия отката**
- >20% users confused by track system
- Progress calculations incorrect (data corruption)
- AI suggestions low quality (>50% negative feedback)
- Performance degradation (>5s for progress updates)

**Шаги отката**
1. Disable `multi_track_system_enabled` flag
2. Bot switches to simple linear flow (existing behavior)
3. Track data preserved in database (не удалять)
4. User може продолжать работать без track visualization

## Риски и митигации

- **Риск 1**: Track system слишком сложный для users - Митигация: simple onboarding, hide complexity, focus на one track at a time
- **Риск 2**: AI suggestions irrelevant - Митигация: context-aware prompts, user feedback loop, manual review
- **Риск 3**: Cross-track impact calculations buggy - Митигация: comprehensive tests, conservative progress deltas
- **Риск 4**: Users игнорируют треки кроме primary - Митигация: periodic suggestions, show benefits, gentle nudges
- **Риск 5**: Performance issues с 4 треками - Митигация: caching, lazy calculations, database indexing

## Параметры стека

**Backend**
- Python 3.11+
- FastAPI (existing)
- SQLAlchemy 2.0 (existing)
- Alembic (migrations)

**AI**
- OpenAI GPT-4 (для next action suggestions)
- LangChain (orchestration)

**Database**
- PostgreSQL 15
- JSON columns для recovery_tracks

**Integration**
- StateManager (existing orchestration layer)
- DatabaseManager (existing)
- Telegram Bot API (existing)

## Самопроверка плана перед выдачей

- ✅ Нет кода (только описание)
- ✅ Все секции заполнены
- ✅ Realistic timeline (17 дней)
- ✅ Integration с existing components described
- ✅ Privacy и security учтены
- ✅ Naming: `IP-05-multi-track-system.md`
