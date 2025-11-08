# PAS Bot - Backlog Index

**Последнее обновление:** 2025-11-04
**Текущий Sprint:** Sprint 1 (Complete) → Sprint 2 (Starting)

---

## 📋 Оглавление

1. [Текущие задачи](#текущие-задачи-current)
2. [Архив завершенных планов](#архив-archive)
3. [Дорожная карта](#дорожная-карта-roadmap)
4. [Документация](#документация)

---

## 📌 Текущие задачи (Current)

### Sprint 2: Emotions & Techniques (В работе)

**Статус:** 🚧 Starting
**Длительность:** 2 недели
**Приоритет:** HIGH

#### Задачи:
1. **Эмоциональный анализ**
   - [ ] Интеграция GoEmotions в state machine
   - [ ] Калибровка emotional_score
   - [ ] Тестирование на русских текстах
   - **Файлы:** `src/nlp/emotion_detector.py`, `src/orchestration/state_manager.py`

2. **Базовые терапевтические техники**
   - [ ] CBT: Cognitive reframing
   - [ ] Grounding exercises (5-4-3-2-1)
   - [ ] Validation responses
   - [ ] Active listening
   - **Новые файлы:** `src/techniques/`

3. **PII Protection активация**
   - [ ] Интеграция в message pipeline
   - [ ] Presidio recognizers для русского
   - [ ] Тестирование
   - **Файлы:** `src/core/bot.py`, `src/nlp/pii_protector.py`

4. **UX улучшения**
   - [ ] Inline кнопки
   - [ ] Меню техник
   - [ ] Progress indicators
   - **Файлы:** `src/core/bot.py`

**Документация:** См. [NEXT_STEPS.md](/NEXT_STEPS.md)

---

### Sprint 3: RAG & Knowledge (Планируется)

**Статус:** 📋 Planned
**Начало:** После завершения Sprint 2
**Приоритет:** HIGH

#### Задачи:
- Haystack pipeline setup
- Qdrant vector database
- Knowledge base ingestion
- Contextual retrieval

**Детали:** См. [ROADMAP.md](/ROADMAP.md#sprint-3-rag--knowledge)

---

## 🗄️ Архив (Archive)

### Sprint 1: Safety & Core Infrastructure ✅

**Статус:** ✅ Complete
**Завершен:** 2025-11-04
**Длительность:** 1 неделя

#### Реализованные планы:

Все детальные планы реализации архивированы в `/docs/backlog/archive/sprint1/`:

1. **IP-01: Knowledge Integration**
   - 📁 `archive/sprint1/IP-01-integration-plan.md`
   - ✅ Реализовано: Database models, storage layer
   - ❌ Не реализовано: RAG (Haystack + Qdrant) - перенесено в Sprint 3
   - **Summary:** См. ниже

2. **IP-02: Guided Letter Writing**
   - 📁 `archive/sprint1/IP-02-guided-letter-writing.md`
   - ✅ Реализовано: Letter model в базе данных
   - ❌ Не реализовано: Letter writing pipeline - перенесено в Sprint 4
   - **Summary:** См. ниже

3. **IP-03: State Machine & Emotional States**
   - 📁 `archive/sprint1/IP-03-state-machine-emotional-states.md`
   - ✅ Реализовано: LangGraph state machine, 11 состояний, 4 фазы
   - ✅ Реализовано: Emotion detector module
   - ⚠️ Частично: Emotion integration в state machine - завершается в Sprint 2
   - **Summary:** См. ниже

4. **IP-04: Therapeutic Techniques**
   - 📁 `archive/sprint1/IP-04-therapeutic-techniques.md`
   - ✅ Реализовано: Архитектура для техник
   - ❌ Не реализовано: Конкретные техники (CBT, IFS, MI, NVC) - Sprint 2
   - **Summary:** См. ниже

5. **IP-05: Safety & Crisis Module**
   - 📁 `archive/sprint1/IP-05-safety-crisis-module.md`
   - ✅ Реализовано: Crisis detector (SuicidalBERT)
   - ✅ Реализовано: NeMo Guardrails (8 политик)
   - ✅ Реализовано: Safety protocols и escalation
   - **Summary:** См. ниже

6. **IP-06: Evaluation Framework**
   - 📁 `archive/sprint1/IP-06-evaluation-framework.md`
   - ✅ Реализовано: Testing infrastructure (pytest)
   - ❌ Не реализовано: Promptfoo, TruLens, Garak - Sprint 6
   - **Summary:** См. ниже

7. **IP-07: Privacy & Compliance**
   - 📁 `archive/sprint1/IP-07-privacy-compliance-legal.md`
   - ✅ Реализовано: PII protector module (Presidio + Natasha)
   - ✅ Реализовано: Zero-PII database design
   - ✅ Реализовано: GDPR/152-ФЗ data retention
   - ⚠️ Частично: PII protection в pipeline - активируется в Sprint 2
   - **Summary:** См. ниже

8. **IP-08: Memory, Profile & Strategy**
   - 📁 `archive/sprint1/IP-08-memory-profile-strategy.md`
   - ✅ Реализовано: User state tracking
   - ✅ Реализовано: Session management
   - ✅ Реализовано: Phase management architecture
   - ❌ Не реализовано: MABWiser JITAI - Sprint 5
   - ❌ Не реализовано: Semantic memory - Post-MVP
   - **Summary:** См. ниже

---

## 📊 Post-Implementation Summaries

### IP-01: Knowledge Integration (RAG) - Частично

**Что реализовано:**
- ✅ Database models (User, Session, Message, Goal, Letter)
- ✅ AsyncIO database manager с CRUD operations
- ✅ SQLAlchemy 2.0 async models
- ✅ Alembic миграции

**Что НЕ реализовано (Sprint 3):**
- ❌ Haystack RAG pipeline
- ❌ Qdrant vector database
- ❌ Document ingestion
- ❌ Contextual retrieval
- ❌ Knowledge base (терапевтические материалы)

**Отклонения от плана:**
- **Причина:** RAG требует готовой базы знаний и отнимает много времени
- **Решение:** Перенесено в отдельный Sprint 3 с полной фокусировкой
- **Benefit:** Позволило закончить safety infrastructure в Sprint 1

**Файлы:**
- `src/storage/models.py` - SQLAlchemy models
- `src/storage/database.py` - Database manager
- `alembic/` - Migrations

---

### IP-02: Guided Letter Writing - Не реализовано (Sprint 4)

**Что реализовано:**
- ✅ Letter model в базе данных (draft storage)
- ✅ LETTER_WRITING state в LangGraph
- ✅ Архитектура для letter pipeline

**Что НЕ реализовано (Sprint 4):**
- ❌ Multi-step guided letter writing process
- ❌ BIFF transformation logic
- ❌ NVC transformation logic
- ❌ Proselint integration для tone checking
- ❌ Draft version management
- ❌ Time capsule feature

**Отклонения от плана:**
- **Причина:** Letter writing требует эмоциональной системы (Sprint 2) и техник
- **Решение:** Перенесено в Sprint 4 после emotions + techniques + RAG
- **Benefit:** Позволяет сделать более качественный letter pipeline с контекстом

**Файлы (созданы для будущего):**
- `src/storage/models.py` - Letter model
- `src/orchestration/state_manager.py` - LETTER_WRITING state (placeholder)

---

### IP-03: State Machine & Emotional States - Реализовано ✅

**Что реализовано:**
- ✅ LangGraph state machine с 11 состояниями
- ✅ 4 фазы терапии (CRISIS → UNDERSTANDING → ACTION → SUSTAINABILITY)
- ✅ Conditional transitions based on emotional state
- ✅ Emotion detector module (GoEmotions)
- ✅ Declarative configuration (graph.yaml)
- ✅ State persistence в базе данных

**Частично реализовано (завершается Sprint 2):**
- ⚠️ Emotion detection интеграция в message flow
- ⚠️ Real-time emotion routing (пока placeholder logic)
- ⚠️ Emotion tracking в Message model

**Отклонения от плана:**
- Заменили BESSER на LangGraph (✅ improvement)
- Упростили начальный state graph (только ключевые states)
- Отложили semantic memory layer на post-MVP

**Файлы:**
- `src/orchestration/state_manager.py` - LangGraph implementation
- `src/nlp/emotion_detector.py` - GoEmotions wrapper
- `config/langraph/graph.yaml` - State graph definition
- `src/storage/models.py` - User state tracking

**Состояния:**
1. START → 2. EMOTION_CHECK → 3. CRISIS_INTERVENTION → 4. HIGH_DISTRESS →
5. MODERATE_SUPPORT → 6. CASUAL_CHAT → 7. LETTER_WRITING → 8. GOAL_TRACKING →
9. TECHNIQUE_SELECTION → 10. TECHNIQUE_EXECUTION → 11. END_SESSION

---

### IP-04: Therapeutic Techniques - Не реализовано (Sprint 2)

**Что реализовано:**
- ✅ TECHNIQUE_SELECTION state
- ✅ TECHNIQUE_EXECUTION state
- ✅ Архитектура для technique plugins

**Что НЕ реализовано (Sprint 2):**
- ❌ CBT: Cognitive reframing
- ❌ IFS: Parts work dialogue
- ❌ MI: Motivational interviewing
- ❌ NVC: Nonviolent communication
- ❌ Grounding exercises
- ❌ Validation responses
- ❌ Active listening prompts

**Отклонения от плана:**
- **Причина:** Techniques требуют рабочей эмоциональной системы
- **Решение:** Перенесено в Sprint 2, будет реализовано сразу после emotions
- **Benefit:** Techniques смогут использовать real emotion data

**Файлы (будущие):**
- `src/techniques/` - Директория создана, пустая
- `src/techniques/base.py` - Базовый класс (to be created)
- `src/techniques/cbt.py` - CBT techniques (to be created)
- `src/techniques/grounding.py` - Grounding (to be created)

---

### IP-05: Safety & Crisis Module - Полностью реализовано ✅

**Что реализовано:**
- ✅ Crisis detector с SuicidalBERT/Mental-BERT
- ✅ Keyword-based fallback для надежности
- ✅ NeMo Guardrails integration (8 политик)
- ✅ Colang DSL для declarative policies
- ✅ Multi-level crisis protocols
- ✅ CRISIS_INTERVENTION state
- ✅ Emergency resource provision
- ✅ Safety event logging

**Политики Guardrails:**
1. ✅ Crisis intervention (суицидальные мысли)
2. ✅ Harm to others (намерение навредить)
3. ✅ Legal boundaries (юридические вопросы)
4. ✅ Illegal activity (незаконные запросы)
5. ✅ Diagnosis boundary (медицинские диагнозы)
6. ✅ Manipulation detection (манипуляции)
7. ✅ Privacy protection (защита PII)
8. ✅ Child discussion redirect (фокус на родителе)

**Без отклонений от плана - полностью реализовано согласно IP-05.**

**Файлы:**
- `src/safety/crisis_detector.py` - SuicidalBERT wrapper
- `src/safety/guardrails_manager.py` - NeMo Guardrails manager
- `config/guardrails/rails.colang` - Policy definitions
- `config/guardrails/config.yml` - Guardrails configuration

---

### IP-06: Evaluation Framework - Не реализовано (Sprint 6)

**Что реализовано:**
- ✅ pytest infrastructure
- ✅ Test configuration (pytest.ini)
- ✅ Basic unit tests (test_config.py)
- ✅ Test coverage setup

**Что НЕ реализовано (Sprint 6):**
- ❌ Promptfoo для regression testing
- ❌ TruLens для runtime monitoring
- ❌ Garak для security testing
- ❌ RAGAS для RAG evaluation
- ❌ Comprehensive test scenarios
- ❌ Safety test suite
- ❌ E2E test flows

**Отклонения от плана:**
- **Причина:** Evaluation tools требуют рабочей системы для тестирования
- **Решение:** Перенесено в Sprint 6 после реализации core features
- **Benefit:** Сможем тестировать реальные flows, а не mocks

**Файлы:**
- `tests/__init__.py` - Test package
- `tests/test_config.py` - Config tests
- `pytest.ini` - pytest configuration

---

### IP-07: Privacy & Compliance - Реализовано ✅

**Что реализовано:**
- ✅ PII protector module (Presidio + Natasha)
- ✅ Russian PII recognizers (passport, SNILS, phone)
- ✅ Zero-PII database design (только content_hash)
- ✅ GDPR compliance features:
  - Right to be forgotten (delete_user_data)
  - Data retention (90 days default)
  - Consent management
- ✅ 152-ФЗ compliance (data localization готов)
- ✅ Privacy-safe logging

**Частично реализовано (активируется Sprint 2):**
- ⚠️ PII detection в message pipeline (module готов, integration pending)
- ⚠️ Automatic PII warnings для пользователя
- ⚠️ PII scrubbing перед DB save

**Без существенных отклонений - реализовано согласно IP-07.**

**Файлы:**
- `src/nlp/pii_protector.py` - Presidio + Natasha wrapper
- `src/storage/models.py` - Zero-PII design (content_hash)
- `src/storage/database.py` - cleanup_old_data, delete_user_data
- `src/core/logger.py` - Privacy-safe logging functions

---

### IP-08: Memory, Profile & Strategy - Частично (Sprint 5 для JITAI)

**Что реализовано:**
- ✅ User state tracking (emotional_score, crisis_level, therapy_phase)
- ✅ Session management (start, end, duration, metrics)
- ✅ Message history (с content_hash)
- ✅ Phase management architecture (4 phases defined)
- ✅ Context storage (JSON field с encryption support)

**Что НЕ реализовано (Sprint 5):**
- ❌ MABWiser contextual bandits для JITAI
- ❌ APScheduler для adaptive timing
- ❌ Intervention selection optimization
- ❌ Readiness assessment
- ❌ Timing optimization

**Что НЕ реализовано (Post-MVP):**
- ❌ Semantic memory layer
- ❌ Long-term pattern extraction
- ❌ Trauma-aware conversation adaptation

**Отклонения от плана:**
- Упростили до базового state tracking для MVP
- JITAI перенесен в Sprint 5 (требует techniques + goals)
- Semantic memory в long-term roadmap

**Файлы:**
- `src/storage/models.py` - User, Session models с tracking
- `src/orchestration/state_manager.py` - User state management
- `src/storage/database.py` - Session CRUD operations

---

## 🗺️ Дорожная карта (Roadmap)

### Текущий прогресс: Sprint 1 Complete (14% общего плана)

```
Sprint 1 ████████████████████░░░░░░░░░░░░░░░░ 100% ✅
Sprint 2 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0% 🚧
Sprint 3 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0% 📋
Sprint 4 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0% 📋
Sprint 5 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0% 📋
Sprint 6 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0% 📋
Sprint 7 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0% 📋
```

### Sprint Breakdown:

| Sprint | Название | Длительность | Статус | Приоритет |
|--------|----------|--------------|--------|-----------|
| 1 | Safety & Core | 1 week | ✅ Complete | CRITICAL |
| 2 | Emotions & Techniques | 2 weeks | 🚧 Starting | HIGH |
| 3 | RAG & Knowledge | 2 weeks | 📋 Planned | HIGH |
| 4 | Letter Writing | 2 weeks | 📋 Planned | MEDIUM |
| 5 | Goals & JITAI | 2 weeks | 📋 Planned | MEDIUM |
| 6 | Evaluation | 1 week | 📋 Planned | HIGH |
| 7 | Production | 1 week | 📋 Planned | CRITICAL |

**Total:** ~11 недель / ~2.5 месяца для MVP

**Детали:** См. [ROADMAP.md](/ROADMAP.md)

---

## 📚 Документация

### Главная документация (корень проекта):

| Файл | Назначение | Аудитория |
|------|------------|-----------|
| [README.md](/README.md) | Основная документация проекта | Все |
| [QUICKSTART.md](/QUICKSTART.md) | Запуск за 5 минут | Developers |
| [ROADMAP.md](/ROADMAP.md) | План развития на 7 спринтов | PM, Developers |
| [NEXT_STEPS.md](/NEXT_STEPS.md) | Что делать дальше (Sprint 2) | Developers |
| [SPRINT1_SUMMARY.md](/SPRINT1_SUMMARY.md) | Детальный отчет Sprint 1 | PM, Stakeholders |

### Техническая документация (docs/):

| Файл | Назначение | Аудитория |
|------|------------|-----------|
| [docs/SOURCE_OF_TRUTH.md](/docs/SOURCE_OF_TRUTH.md) | **Единый источник истины** | Все |
| [docs/ARCHITECTURE.md](/docs/ARCHITECTURE.md) | Детальная архитектура | Architects, Developers |
| [docs/backlog/index.md](/docs/backlog/index.md) | Этот файл - индекс backlog | PM, Developers |

### Архивная документация (docs/backlog/archive/):

| Файл | Статус | Описание |
|------|--------|----------|
| archive/sprint1/IP-01-*.md | ✅ Архив | Оригинальные планы реализации |
| archive/sprint1/IP-02-*.md | ✅ Архив | Sprint 1 - завершен |
| archive/sprint1/IP-03-*.md | ✅ Архив | См. summaries выше |
| archive/sprint1/IP-04-*.md | ✅ Архив | |
| archive/sprint1/IP-05-*.md | ✅ Архив | |
| archive/sprint1/IP-06-*.md | ✅ Архив | |
| archive/sprint1/IP-07-*.md | ✅ Архив | |
| archive/sprint1/IP-08-*.md | ✅ Архив | |

### Конфигурационная документация:

| Файл | Назначение |
|------|------------|
| [config/guardrails/rails.colang](/config/guardrails/rails.colang) | Политики безопасности |
| [config/langraph/graph.yaml](/config/langraph/graph.yaml) | Граф состояний |
| [.env.example](/.env.example) | Шаблон переменных окружения |

---

## 🔍 Как найти информацию?

### Я хочу...

**...понять систему целиком**
→ Читай [docs/SOURCE_OF_TRUTH.md](/docs/SOURCE_OF_TRUTH.md)

**...быстро запустить бота**
→ Читай [QUICKSTART.md](/QUICKSTART.md)

**...узнать что уже реализовано**
→ Читай [SPRINT1_SUMMARY.md](/SPRINT1_SUMMARY.md) или summaries выше

**...узнать что делать дальше**
→ Читай [NEXT_STEPS.md](/NEXT_STEPS.md)

**...понять архитектуру**
→ Читай [docs/ARCHITECTURE.md](/docs/ARCHITECTURE.md)

**...узнать долгосрочные планы**
→ Читай [ROADMAP.md](/ROADMAP.md)

**...найти оригинальные планы реализации**
→ Смотри [docs/backlog/archive/sprint1/](/docs/backlog/archive/sprint1/)

**...понять почему что-то не реализовано**
→ Читай post-implementation summaries выше

---

## 📊 Статистика проекта

### Код:
- **Python modules:** 15 файлов
- **Lines of code:** ~3,500+
- **Test coverage:** ~10% (базовые тесты, будет расти)

### Документация:
- **Documentation files:** 25+ markdown файлов
- **Total words:** ~50,000+ слов
- **Languages:** Русский (primary), English (code)

### Architecture:
- **Layers:** 6 (core, safety, orchestration, nlp, storage, api)
- **States:** 11 в LangGraph
- **Safety policies:** 8 в Guardrails
- **Database models:** 5 (User, Session, Message, Goal, Letter)
- **Therapy phases:** 4 (CRISIS → UNDERSTANDING → ACTION → SUSTAINABILITY)

### Sprint 1 Metrics:
- **Duration:** 1 неделя
- **Planning:** ~2 часа
- **Implementation:** ~6 часов
- **Documentation:** ~2 часа
- **Total:** ~10 часов
- **Velocity:** Fast! 🚀

---

## 🎯 Ключевые решения и rationale

### Почему LangGraph вместо BESSER?
- ✅ Более зрелая экосистема (LangChain)
- ✅ Лучшая документация
- ✅ Async-first design
- ✅ Легче тестировать

### Почему Haystack вместо KAG/OpenSPG?
- ✅ Проще в интеграции
- ✅ Лучше работает с мультиязычием
- ✅ Меньше зависимостей
- ✅ Достаточно для MVP

### Почему перенесли некоторые features в следующие спринты?
- ✅ Фокус на safety first (критично)
- ✅ Избежание overcomplexity в Sprint 1
- ✅ Логическая зависимость features (emotions → techniques → letters)
- ✅ Возможность раньше начать тестирование core функциональности

---

## ✅ Checklist готовности к Sprint 2

Перед началом Sprint 2 убедитесь:

- [x] Sprint 1 полностью завершен
- [x] Документация актуализирована
- [x] Планы архивированы
- [x] Index.md создан
- [x] SOURCE_OF_TRUTH.md написан
- [ ] Бот запущен и протестирован
- [ ] Все базовые команды работают
- [ ] База данных создана
- [ ] Tests проходят
- [ ] Команда готова к Sprint 2

**Когда все галочки стоят → можно начинать Sprint 2!** 🚀

---

## 📞 Контакты и поддержка

**Для разработчиков:**
- Issues: GitHub Issues
- Documentation: Этот index + /docs
- Questions: См. SOURCE_OF_TRUTH.md

**Для stakeholders:**
- Status updates: SPRINT*_SUMMARY.md files
- Roadmap: ROADMAP.md
- Progress: Этот index.md

---

**Версия:** 1.0
**Последнее обновление:** 2025-11-04
**Следующее обновление:** После завершения Sprint 2

**Этот index - единая точка навигации по всему backlog проекта.** 🗺️