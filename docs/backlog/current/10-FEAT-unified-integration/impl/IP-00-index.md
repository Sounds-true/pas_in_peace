# Unified Integration: Implementation Plans Index

## Обзор проекта

Объединение проектов **pas_in_peace** (Telegram-бот для отчужденных родителей) и **inner_edu** (образовательная платформа для детей) в единую экосистему семейного исцеления.

### Ключевые цели

1. **Unified Web Interface** - один веб-интерфейс для управления всеми аспектами recovery journey
2. **Multi-Track Recovery** - параллельное развитие по 4 направлениям с визуализацией прогресса
3. **Quest Builder** - conversational AI для создания персонализированных квестов для детей
4. **"Trojan Horse" Strategy** - reveal mechanics где ребенок постепенно открывает создателя квеста
5. **Privacy-First** - защита данных ребенка, explicit consent, neutral reporting обоим родителям
6. **Shared Database** - единая PostgreSQL база для обоих проектов

## Структура Implementation Plans

Проект разбит на 6 модулей, каждый с детальным implementation plan:

### IP-01: Master Architecture
**Файл**: `IP-01-master-architecture.md`

**Что покрывает**:
- Высокоуровневая архитектура unified системы
- Взаимодействие PAS Bot Backend + Inner Edu Frontend + Shared Database
- Основные user flows (создание квеста, ребенок играет, unified dashboard)
- API contracts между компонентами
- 6-week phased implementation timeline

**Ключевые компоненты**:
- PAS Bot Backend (FastAPI, StateManager, Techniques)
- Inner Edu Frontend (Next.js, React, TypeScript)
- Shared PostgreSQL database
- API Gateway
- Authentication layer

**Timeline**: 6 недель (phases 1-5)

**Dependencies**: None (базовый plan)

---

### IP-02: Web Interface
**Файл**: `IP-02-web-interface.md`

**Что покрывает**:
- Unified dashboard для родителей
- React компоненты (UnifiedDashboard, MultiTrackProgress, CreativeProjects, LetterManager, Analytics)
- WebSocket integration для real-time quest creation dialogue
- Telegram OAuth authentication
- Responsive design (desktop + tablet)

**Ключевые компоненты**:
- ParentDashboard page
- Zustand (global state) + React Query (server state)
- PAS Bot API Client (pasBot.ts)
- Chart.js для analytics
- React Flow для quest visualization

**Timeline**: 17 дней

**Dependencies**: IP-01 (API contracts), IP-03 (WebSocket protocol)

---

### IP-03: Quest Builder Assistant
**Файл**: `IP-03-quest-builder-assistant.md`

**Что покрывает**:
- Conversational AI для создания квестов (QuestBuilderAssistant)
- Multi-stage state machine (INITIAL → GATHERING → GENERATING → REVIEWING → MODERATING → FINALIZING)
- ContentModerator для safety (toxic content detection)
- GPT-4 integration для YAML generation
- WebSocket endpoints для frontend dialogue

**Ключевые компоненты**:
- QuestBuilderAssistant class (inherits from Technique)
- ContentModerator class (pattern + AI-based moderation)
- QuestContext (session state management)
- YAML export для inner_edu

**Timeline**: 17 дней

**Dependencies**: IP-01 (architecture), IP-04 (Quest model), SupervisorAgent (existing)

---

### IP-04: Database Shared Layer
**Файл**: `IP-04-database-shared-layer.md`

**Что покрывает**:
- Shared PostgreSQL schema для обоих проектов
- 6 новых models (Quest, CreativeProject, QuestAnalytics, ChildPrivacySettings, PsychologicalProfile, User extensions)
- Privacy enforcement layer
- DatabaseManager methods (CRUD + privacy checks)
- Alembic migrations

**Ключевые компоненты**:
- Quest model (quest metadata + YAML)
- QuestAnalytics (aggregated child progress, NO personal data)
- ChildPrivacySettings (consent management)
- PsychologicalProfile (unified analytics)
- Foreign key constraints + indexes

**Timeline**: 12 дней

**Dependencies**: IP-01 (architecture), existing User model

---

### IP-05: Multi-Track System
**Файл**: `IP-05-multi-track-system.md`

**Что покрывает**:
- 4 параллельных recovery трека (SELF_WORK, CHILD_CONNECTION, NEGOTIATION, COMMUNITY)
- Track progress visualization
- Milestone system
- AI-powered next action suggestions
- Track switching logic
- StateManager integration

**Ключевые компоненты**:
- MultiTrackManager class
- RecoveryTrack и TrackPhase enums
- TrackProgress TypedDict
- Intent detection (message → track mapping)
- /progress Telegram command
- /api/tracks/* endpoints

**Timeline**: 17 дней

**Dependencies**: IP-01 (architecture), IP-04 (User model extensions), existing StateManager

---

### IP-06: Reveal & Achievement System
**Файл**: `IP-06-reveal-achievement-system.md`

**Что покрывает**:
- "Троянский конь" стратегия (progressive reveal)
- 4 reveal phases (NEUTRAL → SUBTLE_CLUES → INVESTIGATION → REVEAL)
- Achievement system с child consent
- Neutral notifications обоим родителям
- Privacy-first architecture
- Clue detection и detective log

**Ключевые компоненты**:
- RevealEngine class (calculate phases, generate clues)
- AchievementNotifier (send to both parents)
- ShareConsent component (child privacy UI)
- ConsentManager
- RevealMechanics, ClueDetector, DetectiveLog (frontend)

**Timeline**: 17 дней

**Dependencies**: IP-01 (architecture), IP-04 (ChildPrivacySettings), IP-03 (quest creation)

---

## Зависимости между модулями

```
IP-01 (Master Architecture)
  ├──> IP-02 (Web Interface)
  ├──> IP-03 (Quest Builder)
  ├──> IP-04 (Database Layer)
  ├──> IP-05 (Multi-Track System)
  └──> IP-06 (Reveal & Achievement)

IP-04 (Database Layer)
  ├──> IP-03 (Quest model needed)
  ├──> IP-05 (User extensions needed)
  └──> IP-06 (ChildPrivacySettings needed)

IP-03 (Quest Builder)
  └──> IP-06 (quests feed into reveal system)

IP-05 (Multi-Track)
  └──> IP-02 (frontend visualization needed)
```

## Рекомендованный порядок реализации

### Phase 1: Foundation (недели 1-2)
1. **IP-04**: Database Shared Layer
   - Создать все models
   - Alembic migrations
   - Privacy enforcement layer
   - CRUD methods

2. **IP-01** (partial): Setup базовой архитектуры
   - API Gateway
   - Authentication
   - Shared config

### Phase 2: Backend Core (недели 3-5)
3. **IP-05**: Multi-Track System
   - MultiTrackManager
   - StateManager integration
   - /progress command
   - API endpoints

4. **IP-03**: Quest Builder Assistant
   - QuestBuilderAssistant
   - ContentModerator
   - GPT-4 integration
   - WebSocket endpoints

### Phase 3: Frontend (недели 6-8)
5. **IP-02**: Web Interface
   - Unified dashboard
   - All React components
   - WebSocket client
   - Charts & visualization

### Phase 4: Advanced Features (недели 9-11)
6. **IP-06**: Reveal & Achievement System
   - RevealEngine
   - Achievement system
   - Consent management
   - Dual parent notifications

### Phase 5: Integration & Testing (неделя 12)
- End-to-end testing
- Performance optimization
- Security audit
- Documentation

## Суммарный объем работ

**Backend**:
- 6 новых Python классов (MultiTrackManager, QuestBuilderAssistant, ContentModerator, RevealEngine, AchievementNotifier, ClueGenerator)
- 6 новых database models + User extensions
- 15+ новых API endpoints
- 2 Alembic migrations
- WebSocket endpoints
- ~2500 lines of Python code

**Frontend**:
- 1 новая page (ParentDashboard)
- 20+ новых React components
- API client (pasBot.ts)
- State management (Zustand stores)
- WebSocket client
- ~3000 lines of TypeScript/React code

**Testing**:
- ~1000 lines unit tests
- ~500 lines integration tests
- End-to-end test scenarios

**Documentation**:
- 6 implementation plans (this set)
- API documentation (OpenAPI spec)
- Migration guides
- User guides

**Total estimated**: 12 недель full-time development

## Критические требования

**Privacy & Security**:
- Child consent required для sharing
- Default: NO_SHARING
- Aggregated data only (NO personal messages)
- Audit logging всех privacy-sensitive operations
- Content moderation на каждом шаге
- PII detection и protection

**Performance**:
- Dashboard load: <3s
- Quest creation dialogue: <2s per response
- GPT-4 generation: <30s
- Notification delivery: <5s
- Multi-track progress calculation: <50ms

**Reliability**:
- Graceful degradation если OpenAI unavailable
- Auto-save каждые 30s (quest creation)
- WebSocket auto-reconnect
- Transaction isolation для database
- Retry logic для external APIs

**Usability**:
- Mobile responsive (tablet support)
- Clear progress visualization
- Intuitive navigation
- Privacy explanations на детском языке
- Error messages user-friendly

## Feature Flags

Для управления rollout:

- `unified_web_interface_enabled` - весь веб-интерфейс
- `multi_track_system_enabled` - система треков
- `quest_builder_enabled` - создание квестов
- `reveal_mechanics_enabled` - progressive reveal
- `achievement_sharing_enabled` - sharing с родителями
- `strict_moderation` - строгая/мягкая модерация
- `dual_parent_notifications` - notifications обоим parents

## Риски и митигации

**Top 5 рисков**:

1. **OpenAI API rate limits / costs**
   - Митигация: caching, template fallbacks, budget monitoring

2. **Custodial parent discovers и блокирует**
   - Митигация: neutral branding, educational positioning, delayed reveal

3. **Child feels manipulated**
   - Митигация: gentle reveal, emphasis на education, option to stop

4. **Privacy leak**
   - Митигация: strict privacy layer, audit logging, aggregated data only

5. **User confusion (too complex)**
   - Митигация: simple onboarding, progressive disclosure, clear UI

## Метрики успеха

**Technical**:
- API response time <2s (95th percentile)
- Uptime >99%
- Zero privacy violations
- Content moderation accuracy >95%

**Product**:
- >70% quest creation completion rate
- >50% children discover reveal organically
- >30% children grant sharing consent
- <10% custodial parent complaints
- >80% user satisfaction (NPS)

**Business**:
- 100 quests created в первый месяц
- 50 active users в beta
- <$100/day OpenAI costs
- Zero security incidents

## Следующие шаги

1. **Review** всех implementation plans с командой
2. **Prioritize** features (может быть некоторые для v2)
3. **Allocate** ресурсы (developers, timeline, budget)
4. **Setup** development environment
5. **Start** с IP-04 (Database Layer) - foundation

## Контакты и вопросы

- Technical questions: см. соответствующий IP-XX.md файл
- Architecture questions: см. IP-01-master-architecture.md
- Privacy questions: см. IP-04 (database) и IP-06 (consent)
- Frontend questions: см. IP-02-web-interface.md

---

**Последнее обновление**: 2025-11-09
**Версия**: 1.0
**Статус**: Ready for review
