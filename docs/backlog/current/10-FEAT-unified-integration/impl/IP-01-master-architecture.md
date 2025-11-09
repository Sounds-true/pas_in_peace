# Implementation Plan: Unified Integration Architecture

## Смысл и цель задачи

Объединить проекты pas_in_peace (бот для отчужденных родителей) и inner_edu (образовательная игра для детей) в единую экосистему семейного исцеления. Создать unified веб-интерфейс где родитель управляет всеми аспектами: письмами, целями, квестами, прогрессом. Обеспечить seamless интеграцию между Telegram-ботом PAS и веб-приложением inner_edu через shared database и API layer.

## Архитектура решения

### Высокоуровневая структура

Три взаимосвязанных компонента:

**PAS Bot Backend** (существующий)
- `src/orchestration/` - StateManager с multi-track recovery system
- `src/techniques/` - QuestBuilderAssistant, LetterWriting, GoalTracking
- `src/storage/` - Shared database models
- `src/api/` - API endpoints для веб-интерфейса (новый)

**Inner Edu Frontend** (существующий + расширение)
- `frontend/src/components/` - React компоненты
- `frontend/src/components/UnifiedDashboard/` - новый главный интерфейс
- `frontend/src/components/AIQuestBuilder/` - существующий Quest Builder
- `frontend/src/components/LetterManager/` - новый для писем
- `frontend/src/components/ProgressTracker/` - multi-track визуализация

**Shared Layer**
- PostgreSQL database - общая для обоих проектов
- API Gateway - единая точка входа
- Authentication - shared session management

### Ключевые модули

**Backend (pas_in_peace расширение)**
1. `src/api/web_endpoints.py` - FastAPI endpoints для frontend
2. `src/techniques/quest_builder.py` - QuestBuilderAssistant
3. `src/safety/content_moderator.py` - модерация контента квестов
4. `src/storage/models.py` - расширение с Quest, CreativeProject, PsychologicalProfile
5. `src/orchestration/multi_track.py` - RecoveryTrack система

**Frontend (inner_edu расширение)**
1. `frontend/src/pages/ParentDashboard.tsx` - главная страница родителя
2. `frontend/src/components/MultiTrackProgress/` - визуализация 4 треков
3. `frontend/src/components/CreativeProjects/` - hub для квестов/писем
4. `frontend/src/api/pasBot.ts` - client для PAS Bot API

## Полный flow работы функционала

### Scenario 1: Родитель создает квест

1. Родитель открывает веб-интерфейс inner_edu
2. Авторизация через Telegram (OAuth)
3. Dashboard показывает 4 recovery трека и текущий прогресс
4. Родитель выбирает "Создать творческий проект" -> "Квест для ребенка"
5. Открывается conversational AI диалог (QuestBuilderAssistant через WebSocket)
6. AI собирает информацию: возраст ребенка, интересы, семейные воспоминания
7. На каждом шаге ContentModerator проверяет токсичность
8. AI генерирует YAML квеста с GPT-4
9. Родитель видит preview в графовом редакторе (React Flow)
10. Может редактировать узлы вручную или попросить AI изменить
11. Final moderation check перед сохранением
12. Квест сохраняется в shared database
13. Родитель получает link для установки на планшет ребенка
14. Track "Child Connection" обновляет прогресс: квест создан +30%

### Scenario 2: Ребенок проходит квест и делится достижением

1. Ребенок открывает Inner Edu app на планшете
2. Квест презентуется как "образовательная игра" (без упоминания родителя)
3. Ребенок проходит уровни, постепенно видит намеки (семейные фото, шутки)
4. На уровне 7-9 начинает расследовать "кто создал эту игру?"
5. Уровень 10: REVEAL - понимает что это от папы/мамы
6. После решения сложной задачи получает achievement
7. App спрашивает: "Поделиться успехом? Оба родителя получат сообщение"
8. Если "Да" - neutral notification отправляется ОБОИМ родителям через Telegram
9. Analytics обновляются в shared database (aggregated, без personal data)
10. Родитель видит в веб-дашборде: "Максим прошел 3 новых уровня" (+10% прогресс)

### Scenario 3: Управление всеми проектами в одном интерфейсе

1. Родитель заходит в веб-дашборд
2. Левое меню показывает:
   - Multi-track progress (4 трека)
   - Creative Projects (квесты, письма, цели)
   - Analytics (эмоции, метрики, тренды)
   - Resources (группы поддержки, юристы)
3. Вкладка "Creative Projects":
   - Grid view: все квесты, письма, фотоальбомы
   - Фильтры: по типу, статусу, дате
   - Каждый проект показывает прогресс и статус модерации
4. Клик на письмо -> открывается редактор
5. Клик на квест -> открывается Quest Builder (React Flow)
6. Все изменения автоматически сохраняются в database
7. Telegram bot PAS может отправлять уведомления о важных событиях

## API и интерфейсы

### Backend API (FastAPI)

**Authentication**
- `POST /api/auth/telegram` - OAuth авторизация через Telegram
- Параметры: telegram_auth_data
- Возвращает: JWT token, user_id

**Multi-Track Progress**
- `GET /api/tracks/progress` - получить прогресс по всем трекам
- Возвращает: dict с 4 треками, milestones, next actions

**Quest Builder**
- `POST /api/quests/start-creation` - начать создание квеста
- `POST /api/quests/continue` - продолжить диалог с AI
- Параметры: message, quest_context
- Возвращает: AI response, current_stage, moderation_status
- `POST /api/quests/export` - экспортировать YAML
- `GET /api/quests/{quest_id}` - получить квест для редактирования

**Creative Projects**
- `GET /api/projects` - список всех проектов (квесты + письма + цели)
- `GET /api/projects/{id}` - детали проекта
- `PUT /api/projects/{id}` - обновить проект

**Letters**
- `GET /api/letters` - список писем
- `POST /api/letters` - создать новое письмо
- `PUT /api/letters/{id}` - редактировать письмо

**Analytics**
- `GET /api/analytics/child-progress/{quest_id}` - aggregated прогресс ребенка
- `GET /api/analytics/emotional-trends` - emotional tracking данные

### Frontend API Client

**QuestBuilderClient**
- `startQuestCreation()` - инициирует WebSocket connection
- `sendMessage(message)` - отправить сообщение AI
- `getPreview()` - получить preview квеста
- `exportQuest()` - финализировать и экспортировать

**MultiTrackClient**
- `getProgress()` - получить текущий прогресс
- `updatePriority(track)` - изменить primary focus

## Взаимодействие компонентов

```
User (Web Browser)
  |
  | HTTPS
  v
Next.js Frontend (inner_edu)
  |
  | REST API / WebSocket
  v
API Gateway
  |
  +---> PAS Bot Backend (FastAPI)
  |       |
  |       +---> StateManager -> QuestBuilderAssistant
  |       |
  |       +---> ContentModerator (check toxicity)
  |       |
  |       +---> OpenAI API (GPT-4 generation)
  |       |
  |       v
  |   PostgreSQL (Shared Database)
  |       ^
  |       |
  +---> Inner Edu Backend (quest serving)
        |
        v
    Child App (Tablet)
        |
        | (achievements sharing)
        v
    Telegram Bot (notifications to both parents)
```

## Порядок реализации

### Phase 1: Foundation (неделя 1-2)

1. Создать shared database models (Quest, CreativeProject, PsychologicalProfile)
2. Создать миграции Alembic
3. Добавить FastAPI в pas_in_peace (если еще нет)
4. Создать базовые API endpoints для auth и projects list

### Phase 2: Quest Builder Backend (неделя 2-3)

1. Создать QuestBuilderAssistant technique в pas_in_peace
2. Реализовать multi-stage dialogue с StateManager integration
3. Создать ContentModerator для токсичности check
4. API endpoints для quest creation flow
5. YAML generation и export логика

### Phase 3: Web Interface (неделя 3-4)

1. Создать UnifiedDashboard компонент в inner_edu frontend
2. Интегрировать существующий AIQuestBuilder
3. Добавить LetterManager компонент
4. Создать MultiTrackProgress визуализацию
5. Подключить к PAS Bot API

### Phase 4: Child App Integration (неделя 4-5)

1. Добавить reveal mechanics в inner_edu квест engine
2. Реализовать achievement sharing flow
3. Privacy consent screen для ребенка
4. Analytics tracking (aggregated only)

### Phase 5: Testing & Polish (неделя 5-6)

1. End-to-end тестирование full flow
2. UI/UX полировка
3. Performance optimization
4. Documentation

## Критичные граничные случаи

**Moderation failures**
- Если контент токсичен - блокировать deploy квеста
- Показать конкретные проблемные узлы
- Дать возможность редактировать

**API unavailability**
- Если OpenAI API недоступен - graceful degradation
- Показать error message и предложить retry
- Сохранить промежуточный прогресс

**Child privacy**
- Если ребенок не дал consent - никакие данные не шарятся
- Default: все sharing выключено
- Родитель видит только "ребенок не разрешил делиться"

**Database conflicts**
- Если два проекта одновременно пишут в shared table - transaction isolation
- Optimistic locking для quest editing

## Объем работ

### Входит в реализацию

- Shared database models и миграции
- QuestBuilderAssistant conversational AI
- ContentModerator для safety
- FastAPI endpoints для веб-интерфейса
- Unified web dashboard (React)
- Multi-track progress система
- Quest Builder UI integration
- Letter Manager UI
- Child app reveal mechanics
- Achievement sharing system
- Analytics aggregation
- Authentication через Telegram

### Не входит в MVP

- Mobile apps (native iOS/Android)
- Real-time collaboration на квестах
- Video/audio content в квестах
- Advanced analytics dashboards
- Machine learning для recommendations
- Multi-language support
- Белый лейбл для других организаций

## Допущения

- Inner edu уже имеет базовый Quest Builder UI (React Flow)
- PostgreSQL database shared между проектами
- OpenAI API доступен для GPT-4 generation
- Telegram OAuth можно использовать для auth
- Parent и child apps могут работать независимо (offline-first не требуется)

## Открытые вопросы

1. Как организовать deployment? Monorepo или отдельные репозитории?
2. Где хостить shared database - ближе к PAS bot или Inner edu?
3. Нужна ли separate admin панель для модераторов контента?
4. Как управлять feature flags между двумя проектами?
5. Какой механизм для обновления child app на планшете?

## Acceptance Criteria

- Родитель может создать квест через веб-интерфейс за 10-15 минут
- AI корректно собирает информацию в conversational режиме
- ContentModerator блокирует токсичный контент
- Квест экспортируется в валидный YAML для inner_edu
- Ребенок видит квест как "образовательную игру" без упоминания родителя
- Reveal происходит на правильном этапе (70-80% прохождения)
- Achievement sharing работает с consent ребенка
- Оба родителя получают одинаковые neutral notifications
- Веб-дашборд показывает прогресс по всем 4 трекам
- Все creative projects (квесты, письма, цели) управляются в одном интерфейсе

## Definition of Done

- Все API endpoints задокументированы в OpenAPI spec
- Frontend подключен к backend через typed API client
- Database migrations применены
- Логирование всех критичных операций
- Модерация контента работает на каждом этапе
- Feature flags для квест-функционала
- README с инструкциями по запуску unified системы
- Metrics для quest creation, moderation, sharing

## Минимальные NFR для MVP

**Производительность**
- Quest creation dialogue: <2s response time
- GPT-4 generation: <30s для полного квеста
- Dashboard load time: <3s
- Поддержка до 100 одновременных quest creations

**Надежность**
- Graceful degradation если OpenAI unavailable
- Автосохранение прогресса каждые 30 секунд
- Retry logic для API calls с exponential backoff

**Ресурсы**
- Database: до 10000 квестов в MVP
- OpenAI API quota: 100 quest generations/day
- WebSocket connections: до 100 concurrent

## Требования безопасности

- Все API endpoints требуют JWT authentication
- ContentModerator проверяет каждый user input
- Child personal data никогда не логируется
- Quest YAML sanitized перед сохранением (XSS prevention)
- Rate limiting на quest creation: 5/hour per user
- PII detection перед sharing с custodial parent
- Secrets (OpenAI key, DB credentials) только через environment variables

## Наблюдаемость

**Логи**
- Quest creation started/completed
- Moderation checks (passed/failed)
- API errors (with sanitized payloads)
- Child achievement sharing events

**Метрики**
- quest_creations_total (counter)
- moderation_failures_total (counter)
- quest_generation_duration_seconds (histogram)
- active_websocket_connections (gauge)
- child_achievements_shared_total (counter)

**Трассировка**
- Span: quest_creation_flow (от start до export)
- Span: ai_generation (OpenAI call)
- Span: content_moderation

## Релиз

**Feature Flags**
- `unified_web_interface_enabled` - включает веб-дашборд
- `quest_builder_enabled` - включает создание квестов
- `achievement_sharing_enabled` - включает sharing для детей
- `content_moderation_strict` - строгая/мягкая модерация

**План развертывания**
1. Staging: тестирование с 5 alpha-users
2. Beta: открыть для 50 early adopters
3. Production: постепенный rollout (10% -> 50% -> 100%)

## Откат

**Условия отката**
- >30% moderation false positives
- OpenAI API costs превышают budget
- Critical bugs в quest YAML generation
- Child privacy leaks обнаружены

**Шаги отката**
1. Отключить feature flag `quest_builder_enabled`
2. Веб-интерфейс переключается на "Coming soon" режим
3. Существующие квесты остаются доступны (read-only)
4. Telegram bot продолжает работать нормально

## Риски и митигации

- **Риск 1**: OpenAI API rate limits - Митигация: caching, fallback на template-based generation
- **Риск 2**: Токсичный контент проскользнет через модерацию - Митигация: manual review queue, reporting механизм
- **Риск 3**: Child identifiable через quest content - Митигация: strict PII filtering, parent education
- **Риск 4**: Performance degradation с ростом users - Митигация: database indexing, API caching
- **Риск 5**: Custodial parent блокирует app - Митигация: neutral branding, educational positioning

## Параметры стека

**Языки и версии**
- Python 3.11+ (backend)
- TypeScript 5.0+ (frontend)

**Фреймворки**
- FastAPI (backend API)
- Next.js 14 (frontend)
- React 18 (UI components)
- LangChain (AI orchestration)

**База данных**
- PostgreSQL 15
- SQLAlchemy 2.0 (ORM)
- Alembic (migrations)

**Деплой**
- Docker containers
- Kubernetes (опционально)
- Shared PostgreSQL instance

## Самопроверка плана перед выдачей

- ✅ Нет кода и псевдокода
- ✅ Заполнены scope, acceptance, risk, release
- ✅ Именование файла: `IP-01-master-architecture.md`
- ✅ Нет упоминаний секретов и приватных URL
- ✅ Описана интеграция существующих компонентов
- ✅ Учтены оба проекта (pas_in_peace + inner_edu)
