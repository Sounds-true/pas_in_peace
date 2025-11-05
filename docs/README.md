# PAS Bot Documentation

Добро пожаловать в документацию PAS Bot - терапевтического чат-бота для поддержки отчужденных родителей.

---

## 🗺️ Навигация по документации

### Начните здесь:

**Я новый разработчик, хочу понять проект:**
1. Читай [SOURCE_OF_TRUTH.md](SOURCE_OF_TRUTH.md) - единый источник истины
2. Затем [ARCHITECTURE.md](ARCHITECTURE.md) - детальная архитектура
3. Затем [/QUICKSTART.md](/QUICKSTART.md) - быстрый старт

**Я хочу начать разработку:**
1. Читай [/QUICKSTART.md](/QUICKSTART.md) - установка за 5 минут
2. Затем [/NEXT_STEPS.md](/NEXT_STEPS.md) - что делать дальше
3. Затем [backlog/index.md](backlog/index.md) - текущие задачи

**Я PM или stakeholder:**
1. Читай [/ROADMAP.md](/ROADMAP.md) - план развития
2. Затем [/SPRINT1_SUMMARY.md](/SPRINT1_SUMMARY.md) - отчет Sprint 1
3. Затем [backlog/index.md](backlog/index.md) - backlog и прогресс

---

## 📚 Структура документации

### Основные документы (корень проекта):

| Документ | Описание | Аудитория |
|----------|----------|-----------|
| [/README.md](/README.md) | Основная документация проекта | Все |
| [/QUICKSTART.md](/QUICKSTART.md) | Запуск за 5 минут | Developers |
| [/ROADMAP.md](/ROADMAP.md) | План на 7 спринтов | PM, Developers |
| [/NEXT_STEPS.md](/NEXT_STEPS.md) | Инструкции для Sprint 2 | Developers |
| [/SPRINT1_SUMMARY.md](/SPRINT1_SUMMARY.md) | Детальный отчет Sprint 1 | PM, Stakeholders |

### Техническая документация (docs/):

| Документ | Описание | Аудитория |
|----------|----------|-----------|
| **[SOURCE_OF_TRUTH.md](SOURCE_OF_TRUTH.md)** | **🌟 Единый источник истины** | **Все** |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Детальная архитектура | Architects, Developers |
| [backlog/index.md](backlog/index.md) | 🗺️ Индекс backlog | PM, Developers |
| [backlog/current/](backlog/current/) | Текущие задачи | Developers |
| [backlog/archive/](backlog/archive/) | Архив завершенных планов | Reference |

---

## 🎯 Быстрые ссылки

### Для понимания системы:
- **Полное описание:** [SOURCE_OF_TRUTH.md](SOURCE_OF_TRUTH.md)
- **Архитектура:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Технологии:** См. раздел "Tech Stack" в SOURCE_OF_TRUTH.md

### Для разработки:
- **Установка:** [/QUICKSTART.md](/QUICKSTART.md)
- **Следующие шаги:** [/NEXT_STEPS.md](/NEXT_STEPS.md)
- **Текущие задачи:** [backlog/index.md](backlog/index.md)

### Для планирования:
- **Roadmap:** [/ROADMAP.md](/ROADMAP.md)
- **Sprint 1 отчет:** [/SPRINT1_SUMMARY.md](/SPRINT1_SUMMARY.md)
- **Backlog:** [backlog/index.md](backlog/index.md)

---

## 📖 Что реализовано (Sprint 1)

### ✅ Core Infrastructure
- Telegram bot с основными командами
- LangGraph state machine (11 состояний)
- Pydantic Settings конфигурация
- Structured logging (structlog)

### ✅ Safety & Crisis Detection
- SuicidalBERT crisis detector
- NeMo Guardrails (8 политик)
- Multi-layer protection
- Crisis protocols

### ✅ NLP & Privacy
- GoEmotions emotion detector (27 эмоций)
- Presidio + Natasha PII protection
- Zero-PII database design
- GDPR/152-ФЗ compliance

### ✅ Database & Storage
- 5 SQLAlchemy models (User, Session, Message, Goal, Letter)
- Async database manager
- Alembic migrations
- Redis integration

### ✅ Documentation
- 25+ файлов документации
- Единый источник истины
- Comprehensive guides
- Inline docstrings

**Детали:** См. [SPRINT1_SUMMARY.md](/SPRINT1_SUMMARY.md)

---

## 🚀 Что дальше (Sprint 2)

### Приоритеты:
1. **Emotion Integration** - GoEmotions в message flow
2. **Therapeutic Techniques** - CBT, grounding, validation
3. **PII Protection** - Активация в pipeline
4. **UX Improvements** - Inline кнопки, меню

**Детали:** См. [NEXT_STEPS.md](/NEXT_STEPS.md)

---

## 🏗️ Архитектура (кратко)

### 6 слоев системы:

```
Telegram Bot Interface
         ↓
Safety Layer (Crisis + Guardrails)
         ↓
Orchestration (LangGraph State Machine)
         ↓
NLP Layer (Emotions + PII Protection)
         ↓
Therapeutic Layer (Techniques, Letters, Goals)
         ↓
Storage Layer (PostgreSQL + Redis)
```

**Подробно:** См. [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 📊 Статистика проекта

### Code:
- **15 Python modules** (~3,500 строк)
- **6 архитектурных слоев**
- **11 состояний** в state machine
- **8 политик безопасности**

### Documentation:
- **25+ markdown файлов**
- **~50,000 слов**
- **Русский + English**

### Coverage:
- **Test coverage:** ~10% (растет)
- **Documentation coverage:** 100% ✅

---

## 🔍 Как найти нужную информацию?

### По темам:

**Safety & Crisis:**
- Crisis Detection: `src/safety/crisis_detector.py`
- Guardrails: `src/safety/guardrails_manager.py`
- Политики: `config/guardrails/rails.colang`
- Документация: SOURCE_OF_TRUTH.md → "Компоненты безопасности"

**State Machine:**
- Code: `src/orchestration/state_manager.py`
- Config: `config/langraph/graph.yaml`
- Документация: SOURCE_OF_TRUTH.md → "State Machine"

**Emotions & NLP:**
- Emotions: `src/nlp/emotion_detector.py`
- PII: `src/nlp/pii_protector.py`
- Документация: SOURCE_OF_TRUTH.md → "Эмоциональная система"

**Database:**
- Models: `src/storage/models.py`
- Manager: `src/storage/database.py`
- Migrations: `alembic/versions/`
- Документация: SOURCE_OF_TRUTH.md → "Модель данных"

**Configuration:**
- Settings: `src/core/config.py`
- Guardrails: `config/guardrails/`
- LangGraph: `config/langraph/`
- Environment: `.env.example`

---

## 🎓 Обучающие материалы

### Для новых разработчиков:

1. **Start:** [/QUICKSTART.md](/QUICKSTART.md) - установка и запуск
2. **Understand:** [SOURCE_OF_TRUTH.md](SOURCE_OF_TRUTH.md) - полное понимание
3. **Dive deep:** [ARCHITECTURE.md](ARCHITECTURE.md) - детали архитектуры
4. **Code:** [/NEXT_STEPS.md](/NEXT_STEPS.md) - начало разработки

### Для архитекторов:

1. **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
2. **Design decisions:** SOURCE_OF_TRUTH.md → "Архитектурные принципы"
3. **Tech stack:** SOURCE_OF_TRUTH.md → "Технологический стек"
4. **Trade-offs:** backlog/index.md → "Ключевые решения"

### Для PM:

1. **Roadmap:** [/ROADMAP.md](/ROADMAP.md)
2. **Progress:** [backlog/index.md](backlog/index.md)
3. **Sprint reports:** [/SPRINT1_SUMMARY.md](/SPRINT1_SUMMARY.md)
4. **Decisions:** backlog/index.md → "Post-implementation summaries"

---

## ✅ Checklist для онбординга

### Новый разработчик:

- [ ] Прочитал README.md (корень проекта)
- [ ] Прочитал SOURCE_OF_TRUTH.md (полное понимание)
- [ ] Прочитал QUICKSTART.md (установка)
- [ ] Запустил бота локально
- [ ] Прочитал NEXT_STEPS.md (что делать)
- [ ] Изучил backlog/index.md (текущие задачи)
- [ ] Готов к разработке! 🚀

### Новый архитектор/PM:

- [ ] Прочитал SOURCE_OF_TRUTH.md (overview)
- [ ] Прочитал ARCHITECTURE.md (детали)
- [ ] Прочитал ROADMAP.md (план)
- [ ] Изучил backlog/index.md (прогресс)
- [ ] Прочитал SPRINT1_SUMMARY.md (что сделано)
- [ ] Понял архитектурные решения
- [ ] Готов к планированию! 📋

---

## 📞 Поддержка

### Вопросы по документации:
- Проверь [backlog/index.md](backlog/index.md) - может быть там
- Проверь [SOURCE_OF_TRUTH.md](SOURCE_OF_TRUTH.md) - единый источник
- Создай issue с тегом `documentation`

### Технические вопросы:
- Проверь [ARCHITECTURE.md](ARCHITECTURE.md)
- Проверь inline документацию в коде
- Создай issue с тегом `question`

### Предложения по улучшению:
- Создай issue с тегом `enhancement`
- Или Pull Request с изменениями

---

## 🔄 Обновления документации

### Текущая версия: 1.0
### Последнее обновление: 2025-11-04

**История изменений:**
- 2025-11-04: Sprint 1 complete, документация финализирована
- 2025-11-04: Создан единый источник истины (SOURCE_OF_TRUTH.md)
- 2025-11-04: Архивированы планы реализации
- 2025-11-04: Создан индекс backlog (backlog/index.md)

**Следующее обновление:** После завершения Sprint 2

---

## 🌟 Главный документ

**Если сомневаешься - начни с:**

### [SOURCE_OF_TRUTH.md](SOURCE_OF_TRUTH.md)

Это единственный документ, который описывает ВСЁ:
- ✅ Архитектуру
- ✅ Компоненты
- ✅ Технологии
- ✅ Процессы
- ✅ Решения
- ✅ Roadmap

**Всегда актуальный. Всегда полный. Единый источник истины.** 🌟

---

**Версия:** 1.0
**Последнее обновление:** 2025-11-04
**Статус:** ✅ Complete & Up-to-date

**Happy coding!** 🚀