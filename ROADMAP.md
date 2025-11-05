# PAS Bot Development Roadmap

Дорожная карта разработки терапевтического бота для поддержки отчужденных родителей.

## ✅ Sprint 1: Safety & Core Infrastructure (Завершен)

**Длительность:** 1 неделя
**Статус:** ✅ Completed

### Выполнено:
- [x] Базовая структура проекта
- [x] Telegram bot с основными командами
- [x] NeMo Guardrails интеграция
- [x] SuicidalBERT детектор кризисов
- [x] LangGraph state machine (базовая)
- [x] Конфигурация через YAML/Colang
- [x] Структурированное логирование
- [x] Database models и миграции
- [x] Docker setup
- [x] Документация и Quick Start

### Ключевые файлы:
```
src/core/bot.py              # Основной бот
src/safety/crisis_detector.py    # Детекция кризисов
src/safety/guardrails_manager.py # NeMo Guardrails
src/orchestration/state_manager.py # LangGraph
config/guardrails/rails.colang   # Политики безопасности
config/langraph/graph.yaml       # Граф состояний
```

---

## 🚧 Sprint 2: Emotions & Basic Techniques (Текущий)

**Длительность:** 2 недели
**Статус:** 🚧 In Progress
**Приоритет:** HIGH

### Задачи:

#### 2.1 Эмоциональный анализ
- [ ] Интеграция GoEmotions для русского языка
- [ ] Калибровка emotional_score и distress_level
- [ ] Связка с LangGraph для эмоциональных переходов
- [ ] Тестирование на русских текстах

**Файлы:** `src/nlp/emotion_detector.py` (создан, требует интеграции)

#### 2.2 Базовые терапевтические техники
- [ ] CBT: Cognitive reframing
- [ ] Active Listening с рефлексией
- [ ] Grounding exercises для кризисов
- [ ] Validation responses

**Новые файлы:**
```
src/techniques/__init__.py
src/techniques/cbt.py
src/techniques/grounding.py
src/techniques/validation.py
```

#### 2.3 Улучшенное управление сессиями
- [ ] Автоматическое создание сессий
- [ ] Отслеживание эмоциональной динамики
- [ ] Session summary generation
- [ ] Quality metrics

**Обновить:** `src/storage/database.py`

#### 2.4 PII Protection активация
- [ ] Интеграция Presidio в message flow
- [ ] Presidio custom recognizers для русского
- [ ] PII scrubbing в логах
- [ ] Тестирование на русских данных

**Файлы:** `src/nlp/pii_protector.py` (создан, требует активации)

### Критерии приемки:
- ✅ Эмоции детектируются с точностью >75% на тестовых данных
- ✅ 3+ базовых техники работают в диалоге
- ✅ PII не попадает в логи и базу
- ✅ Session metrics собираются корректно

---

## 📋 Sprint 3: RAG & Knowledge Base

**Длительность:** 2 недели
**Статус:** 📋 Planned
**Приоритет:** HIGH

### Задачи:

#### 3.1 RAG Infrastructure
- [ ] Haystack pipeline setup
- [ ] Qdrant vector database
- [ ] Embedding model (multilingual)
- [ ] Document ingestion pipeline

#### 3.2 Knowledge Sources
- [ ] Терапевтические техники (CBT, IFS, MI, NVC)
- [ ] Parental Alienation информация
- [ ] Юридические границы (что можно/нельзя)
- [ ] Ресурсы поддержки (горячие линии, центры)

#### 3.3 Retrieval Integration
- [ ] Контекстуальный retrieval в LangGraph
- [ ] Reranking для релевантности
- [ ] Source attribution в ответах
- [ ] Fallback на LLM знания

#### 3.4 Evaluation
- [ ] RAGAS для оценки RAG quality
- [ ] Relevance scoring
- [ ] Faithfulness checking

### Новые файлы:
```
src/rag/__init__.py
src/rag/haystack_pipeline.py
src/rag/qdrant_store.py
src/rag/document_loader.py
data/rag/knowledge_base/
```

### Критерии приемки:
- ✅ RAG отвечает на 90%+ вопросов о PA
- ✅ Source attribution работает
- ✅ Нет галлюцинаций на критических темах
- ✅ Latency <2s для retrieval

---

## 📝 Sprint 4: Letter Writing Flow

**Длительность:** 2 недели
**Статус:** 📋 Planned
**Приоритет:** MEDIUM

### Задачи:

#### 4.1 Letter Writing Pipeline
- [ ] Multi-step guided process
- [ ] Emotional processing перед написанием
- [ ] Draft generation с LLM
- [ ] Iterative refinement

#### 4.2 BIFF & NVC Transformations
- [ ] BIFF validator и transformer
- [ ] NVC structure checker
- [ ] Tone analysis (Proselint integration)
- [ ] Suggestions engine

#### 4.3 Letter Management
- [ ] Save drafts
- [ ] Version history
- [ ] Time capsule feature
- [ ] Export options (txt, pdf)

#### 4.4 Guardrails для писем
- [ ] PII detection в письмах
- [ ] Aggressive language filter
- [ ] Legal advice warnings
- [ ] Child protection checks

### Новые файлы:
```
src/letters/__init__.py
src/letters/writer.py
src/letters/biff_transformer.py
src/letters/nvc_transformer.py
src/letters/validator.py
```

### Критерии приемки:
- ✅ Письма проходят BIFF принципы
- ✅ NVC структура корректна
- ✅ PII не попадает в финальное письмо
- ✅ Users satisfied с процессом (тестирование)

---

## 🎯 Sprint 5: Goals & JITAI

**Длительность:** 2 недели
**Статус:** 📋 Planned
**Приоритет:** MEDIUM

### Задачи:

#### 5.1 Goal Management
- [ ] SMART goal setting dialogue
- [ ] Milestone tracking
- [ ] Blocker identification
- [ ] Progress visualization

#### 5.2 JITAI System
- [ ] MABWiser contextual bandits
- [ ] Context feature extraction
- [ ] Intervention selection
- [ ] Reward feedback loop

#### 5.3 Scheduling
- [ ] APScheduler integration
- [ ] Check-in reminders
- [ ] Adaptive timing
- [ ] User preference learning

#### 5.4 Phase Manager
- [ ] CRISIS → UNDERSTANDING → ACTION → SUSTAINABILITY
- [ ] Phase transition logic
- [ ] Phase-appropriate interventions
- [ ] Progress tracking по фазам

### Новые файлы:
```
src/goals/__init__.py
src/goals/manager.py
src/goals/smart_validator.py
src/jitai/__init__.py
src/jitai/mabwiser_engine.py
src/jitai/scheduler.py
src/phases/__init__.py
src/phases/phase_manager.py
```

### Критерии приемки:
- ✅ Goals SMART-compliant
- ✅ JITAI показывает improvement над baseline
- ✅ Reminders не раздражают пользователей
- ✅ Phase transitions логичны

---

## 🧪 Sprint 6: Evaluation & Monitoring

**Длительность:** 1 неделя
**Статус:** 📋 Planned
**Приоритет:** HIGH

### Задачи:

#### 6.1 Prompt Testing
- [ ] Promptfoo setup
- [ ] Test cases для всех сценариев
- [ ] Regression tests в CI/CD
- [ ] A/B testing framework

#### 6.2 Runtime Monitoring
- [ ] TruLens integration
- [ ] LangSmith tracing
- [ ] Metrics dashboard
- [ ] Alerting для аномалий

#### 6.3 Security Testing
- [ ] Garak adversarial tests
- [ ] Jailbreak attempts
- [ ] PII leakage tests
- [ ] Guardrails bypass attempts

#### 6.4 Quality Metrics
- [ ] Therapeutic alliance score
- [ ] Emotional shift tracking
- [ ] Goal achievement rate
- [ ] User engagement metrics

### Новые файлы:
```
eval/promptfoo/
eval/promptfoo/config.yaml
eval/test_cases/
monitoring/trulens_config.py
monitoring/dashboards/
```

### Критерии приемки:
- ✅ 95%+ prompts pass regression tests
- ✅ Все critical paths мониторятся
- ✅ Garak не находит критических уязвимостей
- ✅ Метрики собираются в реальном времени

---

## 🚀 Sprint 7: Production Readiness

**Длительность:** 1 неделя
**Статус:** 📋 Planned
**Приоритет:** CRITICAL

### Задачи:

#### 7.1 Performance Optimization
- [ ] Query optimization
- [ ] Connection pooling tuning
- [ ] Caching strategy
- [ ] Load testing

#### 7.2 Security Hardening
- [ ] Secrets management (Vault/AWS Secrets)
- [ ] Rate limiting
- [ ] DDoS protection
- [ ] Penetration testing

#### 7.3 Deployment Automation
- [ ] CI/CD pipeline
- [ ] Kubernetes manifests
- [ ] Helm charts
- [ ] Blue-green deployment

#### 7.4 Observability
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] ELK stack для логов
- [ ] Distributed tracing (Jaeger)

#### 7.5 Documentation
- [ ] API documentation
- [ ] Deployment guide
- [ ] Incident response playbook
- [ ] User manual

### Критерии приемки:
- ✅ <1s response time (p95)
- ✅ 99.9% uptime SLA achievable
- ✅ Security audit passed
- ✅ Zero-downtime deployments работают

---

## 🔮 Future Enhancements (Post-MVP)

### Phase 2 Features:
- Multi-language support (English, Spanish)
- Voice message support
- Group therapy sessions
- Therapist dashboard для supervised mode
- Mobile app (React Native)

### Advanced AI Features:
- Fine-tuned model для PA domain
- Semantic memory layer
- Trauma-aware conversation adaptation
- Predictive intervention timing

### Integrations:
- Calendar integration (Google, Outlook)
- Wearables data (если доступно)
- Legal document templates
- Support group matching

---

## Метрики успеха

### Technical Metrics:
- **Uptime:** >99.5%
- **Response Time:** <2s (p95)
- **Crisis Detection:** >95% recall
- **PII Leakage:** 0%

### Product Metrics:
- **User Retention:** >60% (30 days)
- **Session Quality:** >4.0/5.0
- **Goal Completion:** >40%
- **Crisis Prevention:** Measurable reduction в escalations

### Therapeutic Metrics:
- **Emotional Improvement:** Measurable по session dynamics
- **Therapeutic Alliance:** >3.5/5.0
- **User Satisfaction:** >4.0/5.0
- **Skill Adoption:** >50% users используют learned techniques

---

## Dependencies & Risks

### Technical Dependencies:
- OpenAI API availability
- Telegram API stability
- Database scalability
- Model hosting costs

### Risks:
- **High:** Crisis misdetection → Mitigation: Multi-model ensemble + human escalation
- **Medium:** PII leakage → Mitigation: Multiple layers of protection + auditing
- **Medium:** User dropout → Mitigation: Engagement features + JITAI
- **Low:** API rate limits → Mitigation: Caching + fallback strategies

---

## Team & Resources

### Required Skills:
- Python backend (FastAPI, SQLAlchemy)
- LLM engineering (LangChain, prompt engineering)
- NLP (transformers, spaCy)
- DevOps (Docker, K8s, CI/CD)
- Clinical psychology consultation (for validation)

### Estimated Effort:
- **Total:** ~10-12 недель full development
- **Team Size:** 2-3 engineers + 1 clinical advisor
- **Budget:** API costs ~$500-1000/month (scale dependent)

---

**Last Updated:** 2025-11-04
**Version:** 1.0
**Status:** Sprint 1 Complete, Sprint 2 Starting