# PAS Bot Architecture

## Обзор системы

PAS Bot — терапевтический бот для поддержки родителей, столкнувшихся с отчуждением детей. Система построена на основе современных практик AI-безопасности и терапевтических протоколов.

## Архитектурные принципы

1. **Safety First** - Безопасность пользователя превыше всего
2. **Privacy by Design** - Конфиденциальность встроена в архитектуру
3. **Modularity** - Модульная структура для расширяемости
4. **Observability** - Полная прозрачность работы системы
5. **Declarative Configuration** - Декларативная настройка через YAML/Colang

## Компоненты системы

### 1. Core Layer (Ядро)

**src/core/**
- `bot.py` - Основной Telegram бот
- `config.py` - Управление конфигурацией
- `logger.py` - Структурированное логирование

**Технологии:**
- python-telegram-bot 20.7+
- Pydantic Settings для конфигурации
- structlog для логирования

### 2. Safety Layer (Безопасность)

**src/safety/**
- `crisis_detector.py` - Детекция суицидальных намерений
- `guardrails_manager.py` - Управление политиками безопасности

**Технологии:**
- SuicidalBERT/Mental-BERT для детекции кризисов
- NeMo Guardrails для политик безопасности
- Detoxify для токсичности

**Ключевые возможности:**
- Автоматическая детекция кризисных ситуаций (порог: 0.7)
- Мгновенное предоставление контактов экстренной помощи
- Блокировка опасных тем (насилие, юридические советы)
- Защита от манипуляций

### 3. Orchestration Layer (Оркестрация)

**src/orchestration/**
- `state_manager.py` - Управление состояниями диалога
- `conversation_graph.py` - Граф состояний

**Технологии:**
- LangGraph для state machine
- LangChain для цепочек обработки

**Состояния:**
```
START → EMOTION_CHECK → {
  CRISIS_INTERVENTION (crisis_level > 0.7)
  HIGH_DISTRESS (emotional_score < 0.3)
  MODERATE_SUPPORT (emotional_score < 0.6)
  CASUAL_CHAT (emotional_score >= 0.6)
}
```

### 4. NLP Layer (Обработка языка)

**src/nlp/**
- `emotion_detector.py` - Детекция эмоций
- `pii_protector.py` - Защита персональных данных

**Технологии:**
- GoEmotions (Russian version) для эмоций
- Presidio + Natasha для PII
- spaCy для морфологии

**Эмоции:**
- 27 категорий эмоций
- Классификация по уровню дистресса
- Рекомендации по терапевтическому подходу

### 5. Storage Layer (Хранение данных)

**src/storage/**
- `models.py` - SQLAlchemy модели
- `database.py` - Менеджер базы данных

**Модели:**
- User - Пользователи и их состояние
- Session - Терапевтические сессии
- Message - Сообщения (PII-scrubbed)
- Goal - Цели пользователей
- Letter - Черновики писем

**Технологии:**
- PostgreSQL для хранения
- SQLAlchemy 2.0 (async)
- Alembic для миграций
- Redis для кэширования

### 6. RAG Layer (Знания) - Планируется Sprint 3

**Технологии:**
- Haystack для RAG pipeline
- Qdrant для векторного хранилища
- Sentence Transformers для эмбеддингов

## Декларативная конфигурация

### config/guardrails/rails.colang

Определяет политики безопасности:
```colang
define flow handle_crisis
  user express suicidal thoughts
  bot offer crisis support
  $crisis_handled = True
```

### config/langraph/graph.yaml

Определяет граф состояний:
```yaml
states:
  EMOTION_CHECK:
    tools: [GoEmotions, SuicidalBERT]
    transitions:
      - to: CRISIS_INTERVENTION
        condition: crisis_detected
```

## Поток обработки сообщений

```
User Message
    ↓
[PII Protector] - Детекция и удаление PII
    ↓
[Crisis Detector] - Быстрая проверка на кризис
    ↓
[Guardrails Check] - Проверка политик
    ↓
[Emotion Detector] - Анализ эмоционального состояния
    ↓
[State Manager] - Обработка через LangGraph
    ↓
[Therapeutic Response] - Генерация ответа
    ↓
[Guardrails Output] - Проверка ответа
    ↓
[PII Scrub] - Финальная очистка PII
    ↓
Response to User
```

## Фазы терапии

### Phase 1: CRISIS (1-2 недели)
- Фокус: Стабилизация и безопасность
- Состояния: CRISIS_INTERVENTION, HIGH_DISTRESS
- Техники: Grounding, Resource provision

### Phase 2: UNDERSTANDING (2-4 недели)
- Фокус: Эмоциональная обработка
- Состояния: HIGH_DISTRESS, MODERATE_SUPPORT
- Техники: Active listening, Validation, CBT

### Phase 3: ACTION (4-8 недель)
- Фокус: Развитие навыков
- Состояния: LETTER_WRITING, TECHNIQUE_EXECUTION
- Техники: BIFF, NVC, Goal setting

### Phase 4: SUSTAINABILITY (постоянно)
- Фокус: Поддержание прогресса
- Состояния: GOAL_TRACKING, CASUAL_CHAT
- Техники: Maintenance, Progress review

## Безопасность и конфиденциальность

### Zero-PII Policy
- Клиентская сторона: Токенизация PII перед отправкой
- Серверная сторона: PII удаляется перед сохранением
- Логи: Только хеши и метрики

### Шифрование
- In-transit: TLS 1.3
- At-rest: PostgreSQL encryption
- Keys: HSM или secure key management

### Compliance
- GDPR: Right to be forgotten (delete_user_data)
- 152-ФЗ: Data localization in Russia
- Retention: 90 days default, configurable

## Мониторинг

### Метрики
- Emotional intensity tracking
- Crisis incident count
- Techniques effectiveness
- Goal completion rate
- Session quality scores

### Логирование
- Structured logs (JSON)
- Privacy-safe (no PII)
- Distributed tracing support
- LangSmith/TruLens integration

## Расширяемость

### Плагины (Будущее)
- Custom therapeutic techniques
- Additional safety models
- Alternative LLM providers
- Custom RAG sources

### API (Sprint 4)
- REST API для интеграции
- WebSocket для real-time
- Webhook endpoints

## Производительность

### Оптимизации
- Async operations throughout
- Connection pooling (PostgreSQL, Redis)
- Model caching (LRU)
- Batch processing для аналитики

### Масштабирование
- Horizontal: Multiple bot instances
- Database: Read replicas
- Cache: Redis cluster
- Load balancer для webhook mode

## Тестирование

### Уровни тестов
1. Unit tests - Отдельные компоненты
2. Integration tests - Взаимодействие модулей
3. Safety tests - Кризисные сценарии
4. E2E tests - Полные диалоги

### Инструменты
- pytest для unit/integration
- Promptfoo для prompt regression
- TruLens для runtime quality
- Garak для red teaming

## Deployment

### Development
- Polling mode
- Local PostgreSQL
- Local Redis
- Debug logging

### Production
- Webhook mode
- Managed PostgreSQL
- Redis cluster
- Structured logging
- Health checks
- Metrics export

## Roadmap

### Sprint 1: Safety & Core ✓
- Basic bot structure
- Crisis detection
- Guardrails setup
- LangGraph state machine

### Sprint 2: Emotions & Techniques (2 недели)
- Emotion detection integration
- Basic therapeutic techniques
- Session management

### Sprint 3: RAG & Knowledge (2 недели)
- Haystack + Qdrant setup
- Knowledge base ingestion
- Contextual responses

### Sprint 4: Letters (2 недели)
- Letter writing flow
- BIFF/NVC transformation
- Draft management

### Sprint 5: Goals & JITAI (2 недели)
- Goal tracking
- MABWiser integration
- Adaptive interventions

### Sprint 6: Evaluation (1 неделя)
- Promptfoo setup
- TruLens monitoring
- Garak security tests

### Sprint 7: Production (1 неделя)
- Performance optimization
- Security hardening
- Deployment automation